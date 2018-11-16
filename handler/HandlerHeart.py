#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : HandlerHeart.py
# @Author: Liaop
# @Date  : 2018-11-15
# @Desc  : 心跳包处理类

from handler.HandlerBase import HandlerBase
from common.DataStruct import MessHeart
import time


class HandlerHeart(HandlerBase):
    def handler(self, kind, data, producer_queue):
        # heart = MessHeart()
        # a = heart.unpack(data)
        self._client.lastms = time.time()
        self._logger.info('收到一个来自{}的心跳包'.format(self._client.address))