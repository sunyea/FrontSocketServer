#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : MainServer.py
# @Author: Liaop
# @Date  : 2018-11-14
# @Desc  : 主服务程序，处理IP绑定、监听和消息获取等

import socket
import select
import time, json
from multiprocessing import Queue
from threading import Thread

from common.DataStruct import MessHead, ClientInfo
from handler.HandlerCommon import HandlerCommon
from kafka.KafkaProducer import KafkaProducer
from kafka.KafkaConsumer import KafkaConsumer
from common.Config import Config

config = Config()


class MainServer(object):
    def __init__(self, address, logger, timeout=10, socketnum=32, max_message=1024, heart_timeout=25):
        '''
        类初始化
        :param address: 服务器地址，tuple(ip,port)
        :param logger: 日志类
        :param timeout: epoll超时时间，int
        :param socketnum: server socket允许链接数，int
        '''
        self._address = address
        self._logger = logger
        self._timeout = timeout
        self._socketnum = socketnum
        self._max_message = max_message
        self._heart_timeout = heart_timeout
        self._socket_msg = dict()
        self._producer_queue = dict()
        self._consumer_queue = dict()

    def __init_socket(self):
        '''
        初始化主服务器socket
        :return:
        '''
        try:
            self._mainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._mainSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._mainSocket.bind(self._address)
            self._mainSocket.listen(self._socketnum)
            self._mainSocket.setblocking(False)
            self._epoll = select.epoll()
            self._epoll.register(self._mainSocket.fileno(), select.EPOLLIN | select.EPOLLET)
            self._sockets = dict()
            self._logger.info('服务器启动成功，正在监听：{}'.format(self._address))
        except Exception as e:
            self._logger.error('[MAINSERVER]服务器启动失败，错误：{}'.format(e))
            raise e

    def __init_producer(self, topics):
        '''
        初始化生产者
        :return:
        '''
        try:
            for topic in topics:
                producer = KafkaProducer(config.kafka_hosts, self._logger)
                if producer.init(topic):
                    self._producer_queue[topic] = Queue()
                    th = Thread(target=producer.produce, args=(self._producer_queue[topic],))
                    th.start()
            self._logger.debug('成功初始化生产者线程')
        except Exception as e:
            self._logger.error('[MAINSERVER]初始化生产者错误：{}'.format(e))
            raise e

    def __init_consumer(self, topics):
        '''
        初始化消费者
        :param topics:
        :return:
        '''
        try:
            for topic in topics:
                consumer = KafkaConsumer(config.kafka_hosts, self._logger)
                if consumer.init(topic, 'gp.{}'.format(topic), balance=False):
                    self._consumer_queue[topic] = Queue()
                    th = Thread(target=consumer.consume, args=(self._consumer_queue[topic],))
                    th.start()
            self._logger.debug('成功初始化消费者线程')
        except Exception as e:
            self._logger.error('[MAINSERVER]初始化消费者错误：{}'.format(e))
            raise e

    def __th_queue(self, queue):
        '''
        遍历队列处理消息的线程
        :param queue: 消息队列
        :return:
        '''
        try:
            while True:
                if not queue.empty():
                    value = queue.get(True)
                    if value is None:
                        continue
                    if len(value) == 0:
                        continue
                    if isinstance(value, bytes):
                        value = value.decode()
                    value = value.replace("'", '"').replace('":,', '":"",')
                    js = json.loads(value)
                    fd = js.get('socketfd')
                    kind = js.get('messtype')
                    client = self._sockets.get(fd)
                    if client:
                        handler = HandlerCommon(client, self._logger, None)
                        handler.handler(kind, value)
        except Exception as e:
            self._logger.error('处理消费者队列线程退出：{}'.format(e))
            raise e

    def __init_sender(self, topics):
        '''
        初始化回馈发送者
        :return:
        '''
        try:
            for topic in topics:
                if self._consumer_queue[topic] is not None:
                    th = Thread(target=self.__th_queue, args=(self._consumer_queue[topic],))
                    th.start()
            self._logger.debug('成功初始化反馈发送线程')
        except Exception as e:
            self._logger.error('初始化回馈发送者时错误：{}'.format(e))
            raise e


    def init(self):
        '''
        初始化服务器
        :return:
        '''
        try:
            self.__init_socket()
            self.__init_producer(config.producer_topics)
            self.__init_consumer(config.consumer_topics)
            self.__init_sender(config.consumer_topics)
            return True
        except Exception as e:
            self._logger.error('[MAINSERVER]服务器启动失败，错误：{}'.format(e))
            return False

    def stop(self):
        '''
        停止服务
        :return:
        '''
        try:
            self._epoll.unregister(self._mainSocket.fileno())
            self._epoll.close()
            self._mainSocket.close()
            self._logger.info('服务器已停止。')
            return True
        except Exception as e:
            self._logger.error('服务器停止出错：{}'.format(e))
            return False

    def run(self):
        '''
        启动服务，开始接收信息
        :return:
        '''
        try:
            while True:
                # 遍历socket,删除超时的socket
                del_fds = list()
                d_now = time.time()
                for fd, client in self._sockets.items():
                    if client.islogin:
                        if (d_now - client.lastms) > self._heart_timeout:
                            del_fds.append(fd)
                for fd in del_fds:
                    self._disconnect(fd)

                events = self._epoll.poll(self._timeout)
                if not events:
                    continue
                for fd, event in events:
                    if fd == self._mainSocket.fileno():
                        # 如果是主服务器，则建立链接
                        self._connect()
                    elif event & select.EPOLLHUP:
                        # 客户端断开
                        self._disconnect(fd)
                    elif event & select.EPOLLIN:
                        # 客户端有消息传入
                        client = self._sockets.get(fd, None)
                        if socket is not None:
                            self._recv(client)
                    else:
                        self._logger.error('消息异常')
                self.printClients()
        except Exception as e:
            self._logger.error('轮询异常：{}'.format(e))
            raise e

    def _connect(self):
        '''
        建立新链接
        :return:
        '''
        try:
            connection, address = self._mainSocket.accept()
            # connection.setblocking(False)
            self._epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLET)
            client = ClientInfo(connection, address)
            self._sockets[connection.fileno()] = client
            self._socket_msg[connection.fileno()] = b''
            self._logger.debug('一个新连接：{}'.format(address))
        except Exception as e:
            self._logger.error('建立新链接出错')
            raise e

    def _disconnect(self, fd):
        '''
        关闭连接
        :param fd: socket句柄
        :return:
        '''
        try:
            self._epoll.unregister(fd)
            self._sockets[fd].socket.close()
            del self._sockets[fd]
            self._logger.debug('释放一个连接：{}'.format(fd))
        except Exception as e:
            self._logger.error('断开链接出错')
            raise e

    def _recv(self, client):
        '''
        从socket获取信息，进行了包头检测，以解决粘包和拆包的问题
        :param client: 客户端信息
        :return:
        '''
        try:
            socket = client.socket
            fd = socket.fileno()
            while True:
                data = socket.recv(self._max_message)
                if not data:
                    break
                if len(self._socket_msg[fd]) > 0:
                    data = self._socket_msg[fd] + data
                    self._socket_msg[fd] = b''
                while True:
                    if len(data) >= 8:
                        # 如果取得一个完整的消息头
                        head = MessHead()
                        head.unpack(data)
                        # print('head.mtype:{},head.msize:{}'.format(head.mtype, head.msize))
                        if len(data) >= head.msize:
                            # 如果取得一个完整的消息体
                            body = data[8:head.msize]
                            handler = HandlerCommon(client, self._logger, self._producer_queue)
                            handler.handler(head.mtype, body)
                            if len(data) == head.msize:
                                break
                            data = data[head.msize:]
                        else:
                            self._socket_msg[fd] += data
                            break
                    else:
                        self._socket_msg[fd] += data
                        break
                if len(self._socket_msg[fd]) == 0:
                    break
        except Exception as e:
            self._logger.error('[RECV] 接收信息出错：{}'.format(e))

    def printClients(self):
        print('='*20)
        for fd, client in self._sockets.items():
            print('编号{}的客户端，是否登录：{}，用户账号：{}，最后链接时间：{}'.format(fd, client.islogin, client.userid, client.lastms))
        print('='*20)