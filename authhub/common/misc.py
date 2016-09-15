# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

from django.conf import settings
from commutils.log import log as logging
from commutils.utils import jsonutils
from django.http.response import HttpResponse
from authhub.common.exception import InvalidRequestFormat

LOG = logging.getLogger(__name__)


def func_action_name(newname):
    def decorator(f):
        f.__name__ = newname
        return f
    return decorator


def get_request_data(httprequest):
    '''get params from HTTPRequest
    '''
    return httprequest.data


def build_reply(retbody=None, retcode=0):
    '''build json reply according to retcode and data
    '''
    retbody = {} if retbody is None else retbody
    reply = {
        'retcode': retcode,
        'retbody': retbody
    }
    return jsonutils.dumps(reply)


def json_response(result, retcode=0):
    '''translate result into json HttpResponse, set server name and Cache-Control
    :param result dict: api result
    :return: HttpResponse in Json format
    ''' 
    response = build_reply(result, retcode)
    httpresponse = HttpResponse(response, content_type="application/json")
    if settings.DEBUG:
        httpresponse['Cache-Control'] = 'no-cache'
    httpresponse["Server"] = "authhub"
    return httpresponse


def purify_request_params(request_params, valid_params):
    '''choose valid param options from request_params
    :param request_params dict: api request parameters
    :params valid_params list: list of params that are valid
    :return: all elements that are valid in valid_params
    '''
    for k in request_params.keys():
        if k not in valid_params:
            del request_params[k]


def check_needed_params(request_params, needed_params):
    '''make sure all request_params contains all params in needed_params
    :param request_params dict: api request parameters
    :params needed_params list: list of params that are needed
    :return: raise exception if not all needed params are included
    '''
    for k in needed_params:
        if k not in request_params:
            raise InvalidRequestFormat('param <%s> is needed for this request'
                                       % k)


def get_request_headers(httprequest):
    ''' get httprequest headers
        @param : Django HttpRequest Object
    '''
    authhub_token = httprequest.META['HTTP_X_EAUTH_TOKEN'] \
                  if 'HTTP_X_EAUTH_TOKEN' in httprequest.META else None
    headers = {
        "method": httprequest.method,
        "path": httprequest.path,
        "token_id": authhub_token
    }
    return headers
