#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : HandlerBase.py
# @Author: Liaop
# @Date  : 2018-11-15
# @Desc  : 消息处理基类

class HandlerBase(object):
    def __init__(self, client, logger):
        self._client = client
        self._logger = logger
