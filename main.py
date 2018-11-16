#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : main.py
# @Author: Liaop
# @Date  : 2018-11-14
# @Desc  : 主程序，生成主服务，并建立守护进程

from MainServer import MainServer
from common.Config import Config
import logging

config = Config()


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    server = MainServer(config.servser_address, logger)
    rt = server.init()
    while rt:
        try:
            server.run()
        except Exception as e:
            logger.error('主服务器运行出错：{}'.format(e))
            server.stop()
            rt = server.init()
            if rt:
                logger.info('主服务器重启..')
    logger.info('主服务器停止')


if __name__ == '__main__':
    main()