#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : DataStruct.py
# @Author: Liaop
# @Date  : 2018-11-15
# @Desc  : 定义消息结构体


import struct
import time

def decode(buf):
    if not isinstance(buf, bytes):
        return buf
    try:
        rt = buf.decode('utf-8')
        return rt
    except:
        pass
    try:
        rt = buf.decode('gb2312')
        return rt
    except:
        pass
    try:
        rt = buf.decode('unicode')
        return rt
    except:
        pass
    rt = buf
    return rt

class ClientInfo(object):
    '''
    客户端信息类
    '''
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.userid = None
        self.islogin = False
        self.lastms = time.time()


class MessHead(object):
    '''
    消息头
    struct{
        int mtype,
        int msize
    }
    '''
    def __init__(self):
        self.mtype = None
        self.msize = 0

    def unpack(self, buf):
        if len(buf) < 8:
            return False
        else:
            _msize, _mtype = struct.unpack('@2i', buf[:8])
            if _msize > 0:
                self.mtype = _mtype
                self.msize = _msize
            return True

    def pack(self):
        if (self.mtype is None) or (self.msize <= 0):
            return None
        else:
            buf = struct.pack('@2i', self.msize, self.mtype)
            return buf


class MessLogin(object):
    '''
    登录消息体
    char uid[64]
    char pwd[64]
    '''
    def __init__(self):
        self.mtype = 0
        self.msize = 136
        self.bsize = self.msize-8
        self.uid = None
        self.pwd = None

    def unpack(self, buf):
        if len(buf) < self.bsize:
            return False
        else:
            _uid, _pwd = struct.unpack('@64s64s', buf[:self.bsize])
            self.uid = decode(_uid)
            self.pwd = decode(_pwd)
            return True

    def pack(self):
        if (self.uid is None) or (self.pwd is None):
            return None
        else:
            buf = struct.pack('@2i64s64s', self.msize, self.mtype, self.uid.encode(), self.pwd.encode())
            return buf


class MessRespLogin(object):
    '''
    登录回馈消息体
    int err
    char mid[32]
    char msg[64]
    '''
    def __init__(self):
        self.mtype = 20
        self.msize = 108
        self.bsize = self.msize - 8
        self.errno = None
        self.mid = None
        self.msg = None

    def unpack(self, buf):
        if len(buf) < self.bsize:
            return False
        else:
            _errno, _mid, _msg = struct.unpack('@i32s64s', buf[:self.bsize])
            self.errno = _errno
            self.mid = decode(_mid)
            self.msg = decode(_msg)
            return True

    def pack(self):
        if (self.errno is None) or (self.mid is None) or (self.msg is None):
            return None
        else:
            buf = struct.pack('@3i32s64s', self.msize, self.mtype, self.errno, self.mid.encode(), self.msg.encode())
            return buf


class MessHeart(object):
    '''
    心跳包
    int heart
    '''
    def __init__(self):
        self.mtype = 1
        self.msize = 12
        self.bsize = self.msize - 8
        self.heart = 0

    def unpack(self, buf):
        if len(buf) < self.bsize:
            return False
        else:
            self.heart = struct.unpack('@i', buf[:self.bsize])
            return True

    def pack(self):
        if self.heart == 0:
            return None
        else:
            buf = struct.pack('@3i', self.msize, self.mtype, self.heart)
            return buf

class MessErr(object):
    '''
    错误反馈
    int errno
    char msg[64]
    '''
    def __init__(self):
        self.mtype = 51
        self.msize = 76
        self.bsize = self.msize - 8
        self.errno = None
        self.msg = None

    def unpack(self, buf):
        if len(buf) < self.bsize:
            return False
        else:
            _errno, _msg = struct.unpack('@i64s', buf[:self.bsize])
            self.errno = _errno
            self.msg = decode(_msg)
            return True

    def pack(self):
        if (self.errno is None) or (self.msg is None):
            return None
        else:
            buf = struct.pack('@3i64s', self.msize, self.mtype, self.errno, self.msg)
            return buf
