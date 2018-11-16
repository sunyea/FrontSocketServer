#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File  : KafkaConsumer.py
# @Author: Liaop
# @Date  : 2018-11-16
# @Desc  : 消费者类


from pykafka import KafkaClient
from pykafka.topic import OffsetType
from kafka.KafkaBase import KafkaBase


class KafkaConsumer(KafkaBase):
    def init(self, topic, groupid, consumer_timeout=0, auto_offset_reset=OffsetType.LATEST, balance=True):
        try:
            if topic is None:
                return False
            if len(topic) == 0:
                return False
            if not isinstance(topic, bytes):
                topic = topic.encode(self._encoding)
            if not isinstance(groupid, bytes):
                groupid = groupid.encode(self._encoding)
            client = KafkaClient(hosts=self._hosts)
            if balance:
                self._consumer = (client.topics[topic]).get_balanced_consumer(consumer_group=groupid,
                                                                              auto_offset_reset=auto_offset_reset,
                                                                              consumer_timeout_ms=consumer_timeout,
                                                                              managed=True)
            else:
                self._consumer = (client.topics[topic]).get_simple_consumer(consumer_group=groupid,
                                                                            auto_offset_reset=auto_offset_reset,
                                                                            consumer_timeout_ms=consumer_timeout)
            return True
        except Exception as e:
            self._logger.error('[KAFKA_CONSUMER]初始化消费者时错误：{}'.format(e))
            return False

    def destroy(self):
        if self._consumer is not None:
            self._consumer.stop()

    def consume(self, queue):
        try:
            for msg in self._consumer:
                if msg is not None:
                    value = msg.value.decode(self._encoding)
                    queue.put(value)
        except Exception as e:
            self._logger.error('[KAFKA_CONSUMER]处理消费信息时出错：{}'.format(e))