#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : Config.py
# @Author: Liaop
# @Date  : 2018-11-16
# @Desc  : 系统常量设置


class Config(object):
    def __init__(self):
        self.servser_address = ('192.168.100.72', 10711)
        self.kafka_hosts = '192.168.100.70:9092,192.168.100.71:9092,192.168.100.72:9092'
        self.producer_topics = ['tp.test.common', 'tp.test.common2']
        self.consumer_topics = ['tp.test.common.response', 'tp.test.common2.response']