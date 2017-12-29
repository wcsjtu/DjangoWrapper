# -*- coding: utf-8 -*-

from __future__ import absolute_import
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage


def send(msg, file, expire=None):
    """send message to channel
    params: file, instance of class `ws4redis.publisher.RedisPublisher`
            msg, unicode
            expire, int. duration which msg stored in redis
    """
    file.publish_message(RedisMessage(msg), expire)


def recv(channel, request, facility, audience='any'):
    """asyn recv first msg stored in redis, if no message here, return None
    params: channel, instance of class `ws4redis.publisher.RedisPublisher`
            request, django http reqeust
            facility, a unique string is used to identify the bucket's ``facility``
            audience, Determines the ``audience`` to check for the message, one of ``group``, ``user``, ``session`` or ``any``
    return: string or None
    """
    msg = channel.fetch_message(request, facility, audience)
    return msg