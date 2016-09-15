# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

from commutils.log import log as logging
from commutils.utils import uuidutils
from authhub.common.exception import UserTokenExpired
from commutils.cache.constants import USER_TOKEN_KEY_PREFIX_MEMCACHE
from authhub.context import g_context
from authhub.resources.user import user_lastlogin_time_update


LOG = logging.getLogger(__name__)

def token_create(user_info):
    '''create token resource
    @param user_info: user_info that will be cached in memcache
    @return: token id if success else None
    '''
    retry_time = 0
    while retry_time < 5:
        token_id = uuidutils.generate_uuid()
        if g_context.memclient.set(USER_TOKEN_KEY_PREFIX_MEMCACHE,
                                   token_id,
                                   user_info):
            user_lastlogin_time_update(user_info['id'])
            return token_id
        retry_time += 1
    return None


def token_revoke(token_id):
    '''delete token
    :return: True if success else False
    '''
    return g_context.memclient.delete(USER_TOKEN_KEY_PREFIX_MEMCACHE,
                                      token_id)


def token_renew(token_id, user_info):
    '''renew existing token
    :param user_info dict: user info that will be stored in cache
    :return: True if success else False
    '''
    if g_context.memclient.set(USER_TOKEN_KEY_PREFIX_MEMCACHE,
                               token_id,
                               user_info):
        LOG.debug("Renew token for user <%s> with token id <%s>" % (user_info, token_id))
        return True
    else:
        LOG.debug("Failed to renew token <%s> for user <%s>" % (token_id, user_info))
        return False   


def token_check(token_id):
    '''check whether the token id still exists in cache
    :return: user id of this user if token not expired else None
    '''
    token_info = g_context.memclient.get(USER_TOKEN_KEY_PREFIX_MEMCACHE, token_id)
    if token_info is None:
        LOG.error("token <%s> has expired" % token_id)
        raise UserTokenExpired(message='user token has expired')
    # renew token
    token_renew(token_id, token_info)
    return token_info
