import redis


class RedisClient():
    def __init__(self, host='127.0.0.1', port='6379'):
        '''
            set connection pool for this client
        '''
        self.conntion_pool = redis.ConnectionPool(host=host, port=port, db=0)

    def set(self, key, value, ep_time=0):
        '''
            set key/value to redis
            @param key: key name to set
            @param value: value for the key
            @param ep_time: expire_time(secs) for the key,
                            0 if the key does not expire
            @return: True if the key exists, False if not
        '''

        try:
            redis_cli = redis.Redis(connection_pool=self.conntion_pool)
            if ep_time == 0:
                redis_cli.set(key, value)
            else:
                redis_cli.set(key, value, ep_time)
        except Exception as e:
            # log exception here
            print e
            return False

        return True

    def get(self, key):
        '''
            get key/value from redis
            @param key: key to get value
            @return: the value of the key, None if key does not exist
        '''

        ret = None
        redis_cli = redis.Redis(connection_pool=self.conntion_pool)
        try:
            ret = redis_cli.get(key)
        except Exception as e:
            print e
            # log exception here
            return None

        return ret

    def delete(self, key):
        '''
            @param key: key to delete
            @return: True if key is deleted, False if not
        '''
        redis_cli = redis.Redis(connection_pool=self.conntion_pool)
        try:
            redis_cli.delete(key)
        except Exception as e:
            print e
            return False

        return True

if __name__ == '__main__':
    '''
        test for redis module
    '''
    redis_cli = RedisClient()
    redis_cli.set('name', 'dev')
    print 'get key name %s' % redis_cli.get('name')

    redis_cli.delete('name')
    print 'Try get key name after it is deleted: %s' % redis_cli.get('name')

    redis_cli.set('country', 'china', '2')
    print 'Try get key country: %s' % redis_cli.get('country')

    import time
    time.sleep(3)
    print ('After 3 seconds, the key expired, try get key '
           'country: %s') % redis_cli.get('country')
