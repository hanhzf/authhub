#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

'''memcache key prefix constant
'''
PROJECT_PREFIX = 'AuthHub'


USER_TOKEN_KEY_PREFIX_MEMCACHE = ('%s.UserTokenKey' % PROJECT_PREFIX)

MEMCACHE_KEY_TIMEOUT = {
    USER_TOKEN_KEY_PREFIX_MEMCACHE: 10800,  # 3 hours
}
