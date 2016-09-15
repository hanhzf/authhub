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
from authhub.common.misc import json_response, get_request_data,\
    check_needed_params, func_action_name
from rest_framework import viewsets
from authhub.resources.token import token_create, token_check, token_revoke
from authhub.resources.user import get_user_by_username, user_password_validate,\
    user_role_list
from authhub.common.exception import ActionPermissionDenied, DBEntryNotExist,\
    IncorrectUserOrPasswd, InternalServerFailure
from authhub.policy.policy_tools import policy_protected
LOG = logging.getLogger(__name__)


class TokenViewSet(viewsets.ViewSet):

    @policy_protected
    @func_action_name("token_create")
    def create(self, request):
        '''create token with username and password
        :param METHOD: POST
        :param URLPATH: /v1/tokens/
        :param dict:
            ::
    
                {
                    'username': USER_NAME,
                    'password': PASSWORD
                }

        :return:
            ::

                {
                    "token_id": TOKEN_ID,
                    "user_id": USER_ID
                }

        '''
        # 1) check all needed parameters are provided
        request_params = get_request_data(request)
        check_needed_params(request_params, ['username', 'password'])    
        # 2) check user exists
        try:
            api_reply = get_user_by_username(request_params['username'])
        except DBEntryNotExist:
            raise IncorrectUserOrPasswd()
        # 3) check user status
        if api_reply['status'] != 'ACTIVE':
            raise ActionPermissionDenied('user has been disabled')
        # 4) check password correct
        user_password_validate(api_reply['id'], request_params['password'])
        # 5) create token and save token,user_info to memcache
        user_roles = [ r['name'] for r in user_role_list(api_reply['id'])]
        user_info = {
            "id": api_reply['id'],
            "username": api_reply['username'],
            "type": api_reply['type'],
            "role": user_roles,
            "email": api_reply['email'],
            "description": api_reply['description'],
        }
        
        token_id = token_create(user_info)
        if not token_id:
            raise InternalServerFailure("Failed to create token for user <%s>"
                                        % user_info['id'])
        # 6) return token_id and user_id
        result = {'token_id': token_id, 'user_id': user_info['id']}
        return json_response(result)

    @policy_protected
    @func_action_name("token_check")
    def retrieve(self, request, pk=None):
        '''check whether token has expired or not
        :param METHOD: GET
        :param URLPATH: /v1/tokens/{token_id}/

        :return: if token is not expired, return
            ::

                {
                    "id": USER_ID,
                    "username": USER_NAME,
                    "type": USER_TYPE,
                    "role": USER_ROLES_LIST,
                    "email": USER_EMAIL,
                    "description": USER_DESCRIPTION,
                }

        else return errorcode 1006 and message "user token has exipired" message to api client
        '''
        token_id = pk
        token_info = token_check(token_id)
        return json_response(token_info)

    @policy_protected
    @func_action_name("token_revoke")
    def destroy(self, request, pk=None):
        '''revoke user's token
        :param METHOD: DESTROY
        :param URLPATH: /v1/tokens/{token_id}/
        :returns: {}
        '''
        token_id = pk
        token_info = token_check(token_id)
        if token_info is not None and not token_revoke(token_id):
            LOG.error("Failed to delete token %s" % token_id)
            raise InternalServerFailure(message=("Failed to delete token %s" % token_id))

        return json_response(None)
