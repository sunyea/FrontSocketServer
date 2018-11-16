#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : KafkaBase.py
# @Author: Liaop
# @Date  : 2018-11-15
# @Desc  : Kafka基础类


class KafkaBase(object):
    def __init__(self, hosts, logger, encoding='utf-8'):
        self._logger = logger
        self._hosts = hosts
        self._encoding = encoding
