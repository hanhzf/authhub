#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

from commutils.cache.constants import MEMCACHE_KEY_TIMEOUT
from commutils.cache import memclient
from commutils.log import log as logging

LOG = logging.getLogger(__name__)


class McModel():
    '''
        this mc model is used to set value for key with prefix in memcache
    '''

    def __init__(self, url, argument={}):
        '''
            initialize mcmodel with memclient
        '''
        self.mc = memclient.MemcacheClient(url, argument)

    def _full_key_name(self, prefix, key):
        '''
            each key has a prefix and key name, prefix will be used to get
            expire time from MEMCACHE_KEY_TIMEOUT
        '''
        return '%s.%s' % (prefix, key)

    def set(self, prefix, key, value, timeout=None):
        '''
            set key value
        '''
        if not timeout and not MEMCACHE_KEY_TIMEOUT.get(prefix):
            LOG.error('failed to get timeout value for prefix: %s' % prefix)
            return False
        timeout = timeout if timeout else MEMCACHE_KEY_TIMEOUT.get(prefix)
        return self.mc.set(self._full_key_name(prefix, key), value, timeout)

    def get(self, prefix, key):
        '''
            get key value
        '''
        return self.mc.get(self._full_key_name(prefix, key))

    def delete(self, prefix, key):
        '''
            delete key from memcache
        '''
        return self.mc.delete(self._full_key_name(prefix, key))
