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
from authhub.resources.group import group_user_list, group_user_add,\
    group_user_delete
from authhub.policy.policy_tools import policy_protected

LOG = logging.getLogger(__name__)


class GroupUserViewSet(viewsets.ViewSet):

    @policy_protected
    @func_action_name("group_user_list")
    def list(self, request, group_pk=None):
        '''list users of existing group
        :param METHOD: GET
        :param URLPATH: /v1/groups/{group_id}/users/
        :return groups's user list:
            ::

                [{'id': '22', 'username': 'user1'}, ...]

        '''
        result = group_user_list(group_pk)
        return json_response(result)

    @policy_protected
    @func_action_name("group_user_add")
    def create(self, request, group_pk=None):
        '''add users to group
        :param METHOD: POST
        :param URLPATH: /v1/groups/{group_id}/users/
        :param dict: {'user_id': USER_ID}
        :return:
            ::

                {
                    "group_id": GROUP_ID,
                    "user_id": USER_ID,
                    "created_at": GROUP_USER_ADD_TIME
                }

        '''
        reqparams = get_request_data(request)
        check_needed_params(reqparams, ['user_id'])
        result = group_user_add(group_pk, reqparams['user_id'])
        return json_response(result)

    @policy_protected
    @func_action_name("group_user_delete")
    def destroy(self, request, pk=None, group_pk=None):
        '''delete user from group
        :param METHOD: DELETE
        :param URLPATH: /v1/groups/{group_id}/users/{user_id}/
        :return: {}
        '''
        group_id, user_id = (group_pk, pk)
        group_user_delete(group_id, user_id)
        return json_response(None)
