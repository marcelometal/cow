#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from redis.sentinel import Sentinel

from cow.plugins.redis_plugin import RedisPlugin, CowRedisClient


class RedisSentinelPlugin(RedisPlugin):

    @classmethod
    def after_start(cls, application, io_loop=None, *args, **kw):
        sentinel_hosts = application.config.get('REDISSENTINELHOSTS')
        sentinel = Sentinel(sentinel_hosts, socket_timeout=0.1)
        host, port = sentinel.discover_master(
            application.config.get('REDISMASTER')
        )

        logging.info('Connecting to redis at %s:%d' % (host, port))

        application.redis = CowRedisClient(io_loop=io_loop)
        application.redis.authenticated = False
        application.redis.connect(
            host,
            port,
            callback=cls.has_connected(application, application.redis)
        )

        if application.config.REDISPUBSUB:
            application.redis_pub_sub = CowRedisClient(io_loop=io_loop)
            application.redis_pub_sub.authenticated = False
            application.redis_pub_sub.connect(
                host,
                port,
                callback=cls.has_connected(
                    application, application.redis_pub_sub
                )
            )

    @classmethod
    def define_configurations(cls, config):
        config.define('REDISDB', 0, 'Redis server database index', 'Redis')
        config.define('REDISPASS', None, 'Redis server database password', 'Redis')
        config.define(
            'REDISPUBSUB',
            False,
            'Indicates whether a second connection to Redis server should be created for pubsub',
            'Redis'
        )
        config.define('REDISMASTER', None, 'Redis master name', 'Redis')
        config.define('REDISSENTINELHOSTS', [], 'Redis sentinel hosts', 'Redis')
