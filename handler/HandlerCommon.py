#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : HandlerCommon.py
# @Author: Liaop
# @Date  : 2018-11-15
# @Desc  : 通用处理类

from common.DataKind import MessType
from handler.HandlerLogin import HandlerLogin
from handler.HandlerHeart import HandlerHeart
from threading import Thread


class HandlerCommon(object):
    def __init__(self, client, logger, producer_queue):
        self._client = client
        self._logger = logger
        self._producer_queue = producer_queue

    def handler(self, ikind, data, h_async=True):
        '''
        通用处理函数
        :param kind: 消息类别
        :param data: 消息体
        :param h_async: 是否异步处理
        :return:
        '''
        try:
            try:
                kind = MessType(ikind)
            except:
                kind = MessType.MessNoType
            handler = None
            if kind == MessType.MessLogin:
                handler = HandlerLogin(self._client, self._logger)
            if kind == MessType.MessRespLogin:
                handler = HandlerLogin(self._client, self._logger)
            elif kind == MessType.MessHeart:
                handler = HandlerHeart(self._client, self._logger)
            else:
                self._logger.error('[HANDLERCOMMON] 未知消息：{}'.format(ikind))
            if handler is not None:
                if h_async:
                    t = Thread(target=handler.handler, args=(kind, data, self._producer_queue))
                    t.start()
                else:
                    handler.handler(kind, data, self._producer_queue)
        except Exception as e:
            self._logger.error('处理信息出错')
            raise e