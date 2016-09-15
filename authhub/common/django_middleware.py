# -*- coding: utf-8 -*-
#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#
from commutils.exception import ZenException
from authhub.common.misc import json_response
from authhub.common.error_code import INTERNAL_SERVER_FAILURE

'''
    writing customized django middle ware here
'''
from commutils.log import log as logging

LOG = logging.getLogger(__name__)


class AuthHubMiddleware(object):
    def __init__(self):
        pass

    def process_request(self, request):
        '''check session
        @return: redirect to login page if there is no session info or
                session expired
                return None if session info exists
        '''
        return None

    def process_reponse(self, request, response):
        '''json format response
        '''
        return None

    def process_exception(self, request, exception):
        if not isinstance(exception, ZenException):
            LOG.exception(exception)
            return json_response("Internal server failure", INTERNAL_SERVER_FAILURE)
        return json_response(exception.message, exception.error_code)
