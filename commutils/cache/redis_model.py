#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

from commutils.redis import redis_client


class RedisModel():
    '''
        Redis model for application
    '''
    def __init__(self, redis_client):
        '''
            @param redis_client: The redis client class used
                                 for communication with redis
        '''
        self.redis_client = redis_client.RedisClient()

    def set(self, key_prefix, key, value, expire_time):
        '''
            generate the key with key_prefix+key, and set value for it
        '''
        redis_key = key_prefix + '.' + key
        return self.redis_client.set(redis_key, value, expire_time)

    def get(self, key_prefix, key):
        '''
            get the value for key key_prefix + key
        '''
        redis_key = key_prefix + '.' + key
        return self.redis_client.get(redis_key)
