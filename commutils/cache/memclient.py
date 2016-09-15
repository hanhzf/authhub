from commutils.cache import mcpool
from commutils.log import log as logging

LOG = logging.getLogger(__name__)


class MemcacheClient():
    '''
        memcached client
    '''

    def __init__(self, url, argument={}):
        self.mcpool = mcpool.PooledMemcachedBackend(url, argument)

    def set(self, key, val, time=60, min_compress_len=0):
        '''
            @return: True if set success
        '''
        try:
            ret = self.mcpool.client.set(str(key), val, time, min_compress_len)
            if ret == 0:
                LOG.error('Failed to set <%s> for <%s>' % (val, key))
                return False
        except Exception, e:
            print e
            LOG.error('memcached client set failed with error %s' % e)
            return False
        return True

    def set_multi(self, mapping, time=60, key_prefix='', min_compress_len=0):
        '''
            @return: True if all mapping are stored to memcached
                     False if not all mapping are stored successfully
        '''
        mapping_keys = set(mapping.keys())
        try:
            ret = self.mcpool.clientpool.client.set_multi(mapping_keys,
                                                          time,
                                                          key_prefix,
                                                          min_compress_len)
            if len(ret) != 0:
                LOG.error('Failed to set_multi for <%s>' % mapping)
                return False
        except Exception, e:
            LOG.error("Failed to set_multi for <%s> with error: <%s>"
                      % (mapping, e))
            return False
        return True

    def get(self, key):
        '''
            @return: None if failed to get value
        '''
        try:
            ret = self.mcpool.client.get(str(key))
        except Exception, e:
            LOG.error('memclient failed to get: %s' % e)
            LOG.exception(e)
            return None
        return ret

    def get_multi(self, keys, key_prefix=''):
        '''
            @param keys: key lists
            @return: None if failed
        '''
        try:
            ret = self.mcpool.client.get_multi(keys, key_prefix)
        except Exception, e:
            LOG.error("" % e)
            return None
        return ret

    def incr(self, key, delta=1):
        ''' increase value
            @param key: key must be str type.
            @param delta: Integer amount to increment by
                          (should be zero or greater).
            @return: New value after incrementing or
                     None if incrementing failed.
            Note: key must existed and its value must in non-negative integer
                  before you can increment it.
        '''
        try:
            ret = self.mcpool.client.incr(str(key), delta)
            if ret is None or ret == 0:
                LOG.error("memcache client incr [%s] failed" % (key))
                return None
        except Exception, e:
            LOG.error("memcache client incr failed: %s" % e)
            return None
        return ret

    def decr(self, key, delta=1):
        ''' decr value
            @param key: key must be str type.
            @param delta: Integer amount to decrement
                          by (should be zero or greater).
            @return: New value after decrementing
                     or None if decrementing failed..
            Note: key must existed and its value must in non-negative integer
                  before you can decrement it.
        '''
        try:
            ret = self.mcpool.client.decr(str(key), delta)
            # Note: sometimes ret = 0 means decr failed but we ignore it here.
            if ret is None:
                LOG.error("memcache client decr [%s] failed" % (key))
                return None
        except Exception, e:
            LOG.error("memcache client decr failed: %s" % e)
            return None
        return ret

    def add(self, key, val, time=60, min_compress_len=0):
        ''' add key-value, like set, but only stores in memcache
            if the key doesn't already exist.
            @param key: key must be str type.
            @param time: a delta number of seconds which
                         this value should expire,
                         default is 60s and time = 0 means cache forever.
            @return: True on success and False on failed.
        '''
        try:
            ret = self.mcpool.client.add(str(key), val, time, min_compress_len)
            if ret == 0:
                LOG.error("memcache client add [%s,%s] failed" % (key, val))
                return False
        except Exception, e:
            LOG.error("memcache client add failed: %s" % e)
            return False
        return True

    def delete(self, key, time=0):
        ''' delete a key
            @param key: key must be str type.
            @param time: number of seconds any subsequent set / update commands
                         should fail. Defaults to None for no delay.
            @return: True on success and False on failed.
        '''
        try:
            ret = self.mcpool.client.delete(str(key), time)
            if ret == 0:
                LOG.error("memcache client delete [%s] failed" % (key))
                return False
        except Exception, e:
            LOG.error("memcache client delete failed: %s" % e)
            return False
        return True
