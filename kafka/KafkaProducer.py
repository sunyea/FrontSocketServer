#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : KafkaProducer.py
# @Author: Liaop
# @Date  : 2018-11-16
# @Desc  : 生产者类


from pykafka import KafkaClient
from pykafka.common import CompressionType
from kafka.KafkaBase import KafkaBase


class KafkaProducer(KafkaBase):
    def init(self, topic, compression=CompressionType.GZIP, linger_ms=0):
        '''
        初始化生产者
        :param topic: 主题名
        :param compression: 压缩方式
        :param linger_ms: 等待发出时间
        :return:
        '''
        try:
            if topic is None:
                return False
            if len(topic) == 0:
                return False
            if not isinstance(topic, bytes):
                topic = topic.encode(self._encoding)
            client = KafkaClient(hosts=self._hosts)
            self._producer = (client.topics[topic]).get_producer(compression=compression, linger_ms=linger_ms)
            return True
        except Exception as e:
            self._logger.error('[KAFKA_PRODUCER]初始化生产者错误：{}'.format(e))
            return False

    def destroy(self):
        if self._producer is not None:
            self._producer.stop()

    def produce(self, queue):
        try:
            while True:
                if not queue.empty():
                    value = queue.get(True)
                    if not isinstance(value, bytes):
                        value = value.encode(self._encoding)
                    self._producer.produce(value)
        except Exception as e:
            self._logger.error('[KAFKA_PRODUCER]生产者发送信息出错：{}'.format(e))