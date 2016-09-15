# -*- coding: utf-8 -*-
#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

import functools
from authhub.context import g_context
from authhub.resources.token import token_check
from commutils.log import log as logging
from authhub.common.misc import get_request_headers
from authhub.common.exception import ActionPermissionDenied
LOG = logging.getLogger(__name__)


def policy_protected(f):
    """wraps api with policy based access
    """
    @functools.wraps(f)
    def inner(self, request, *args, **kwargs):
        action = 'identity:%s' % f.__name__
 
#         req_header = get_request_headers(request)
#         token_id = req_header['token_id']
#         if token_id is None:
#             raise ActionPermissionDenied(u'please provide correct token')
#         auth_info = token_check(token_id)
#  
#         g_context.policyChecker.enforce(action, auth_info)
        return f(self, request, *args, **kwargs)
    return inner
