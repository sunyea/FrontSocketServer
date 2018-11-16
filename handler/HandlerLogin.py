#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : HandlerLogin.py
# @Author: Liaop
# @Date  : 2018-11-15
# @Desc  : 登录处理类

from handler.HandlerBase import HandlerBase
from common.DataStruct import MessLogin, MessRespLogin
from common.DataKind import MessType
import time, json


class HandlerLogin(HandlerBase):
    def handler(self, kind, data, producer_queue):
        if kind == MessType.MessLogin:
            print('收到登录消息')
            self.handler_checklogin(kind.value, data, producer_queue)
        elif kind == MessType.MessRespLogin:
            print('收到登录反馈')
            self.handler_resplogin(data)

    def handler_checklogin(self, kind, data, producer_queue):
        topic = 'tp.test.common'
        try:
            login = MessLogin()
            if login.unpack(data):
                self._logger.info('账号：{}，密码：{}'.format(login.uid, login.pwd))
                # 组合发到kafka的json
                js = json.dumps({'socketfd': self._client.socket.fileno(), 'userid': self._client.userid, 'messtype': kind, 'data': {'uid': login.uid, 'pwd': login.pwd}})
                producer_queue[topic].put(js)
            else:
                e = Exception('不是正确的消息包')
                raise e
        except Exception as e:
            self._logger.error('[HANDLE_LOGIN]验证登录出错：{}'.format(e))
            raise e

    def handler_resplogin(self, data):
        js_resp = json.loads(data)
        resp_login = MessRespLogin()
        resp_login.errno = int(js_resp.get('code'))
        resp_login.mid = 'managerid'
        resp_login.msg = js_resp.get('err')
        send_buf = resp_login.pack()
        if send_buf is None:
            return
        if not isinstance(send_buf, bytes):
            send_buf = send_buf.encode('utf-8')
        self._client.socket.send(send_buf)

