# -*- coding: utf-8 -*-
#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

from rest_framework import viewsets
from commutils.log import log as logging
from authhub.common.misc import json_response, get_request_data,\
    check_needed_params, func_action_name
from authhub.resources.user import user_role_list, user_role_grant,\
    user_role_revoke
from authhub.policy.policy_tools import policy_protected

LOG = logging.getLogger(__name__)


class UserRoleViewSet(viewsets.ViewSet):

    @policy_protected
    @func_action_name("user_role_list")
    def list(self, request, user_pk=None):
        '''list role of all existing users
        :param METHOD: GET
        :param URLPATH: /v1/users/{user_id}/roles/
        :return user's role list:
            ::

                ['role1', 'role2', ...]

        '''
        result = user_role_list(user_pk)
        return json_response(result)

    @policy_protected
    @func_action_name("user_role_grant")
    def create(self, request, user_pk=None):
        '''grant roles to user
        :param METHOD: POST
        :param URLPATH: /v1/users/{user_id}/roles/
        :param dict: {'rolename': ROLE_NAME}
        :return:
            ::

                {
                    "user_id": USER_ID,
                    "role_id": TOKEN_ID,
                    "created_at": USER_ROLE_ADD_TIME
                }

        '''
        reqparams = get_request_data(request)
        check_needed_params(reqparams, ['rolename'])
        result = user_role_grant(user_pk, reqparams['rolename'])
        return json_response(result)

    @policy_protected
    @func_action_name("user_role_revoke")
    def destroy(self, request, pk=None, user_pk=None):
        '''revoke roles from user
        :param METHOD: DELETE
        :param URLPATH: /v1/users/{user_id}/roles/{role_id}/
        :return: {}
        '''
        user_id, role_id = (user_pk,pk)
        user_role_revoke(user_id, role_id)
        return json_response(None)
