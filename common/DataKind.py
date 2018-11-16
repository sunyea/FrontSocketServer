#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : DataKind.py
# @Author: Liaop
# @Date  : 2018-11-15
# @Desc  : 定义消息类别


from enum import Enum


class MessType(Enum):
    MessNoType = -1         # 未知消息类别
    MessLogin = 0           # 客户端登录
    MessRespLogin = 20      # 客户端登录回复

    MessHeart = 50          # 心跳包
    MessErr = 51            # 错误反馈