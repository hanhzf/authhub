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
    func_action_name
from authhub.resources.group import group_create, group_list,\
    group_delete, get_group_by_id, group_update
from authhub.policy.policy_tools import policy_protected

LOG = logging.getLogger(__name__)


class GroupViewSet(viewsets.ViewSet):

    @policy_protected
    @func_action_name("group_list")
    def list(self, request):
        '''list of all existing groups
        :param METHOD: GET
        :param URLPATH: /v1/groups/

        :returns list:
            ::

                [
                    {
                        'id': GROUP_ID,
                        'groupname': GROUP_NAME,
                        'created_at': GROUP_CREATE_TIME
                    },
                    {
                        'id': GROUP_ID,
                        'groupname': GROUP_NAME,
                        'created_at': GROUP_CREATE_TIME
                    },
                    ......
                ]

        '''
        reqparams = get_request_data(request)
        result = group_list(reqparams)
        return json_response(result)

    @policy_protected
    @func_action_name("group_create")
    def create(self, request):
        '''create new groups
        :param METHOD: POST
        :param URLPATH: /v1/groups/
        :param dict:
            ::

                {
                    'groupname': GROUP_NAME,
                    'type': GROUP_TYPE,
                    'description': GROUP_DESCRIPTION
                }

        :returns:
            ::

                {
                    'id': GROUP_ID,
                    'groupname': GROUP_NAME
                }

        '''
        reqparams = get_request_data(request)
        result = group_create(reqparams)
        return json_response(result)

    @policy_protected
    @func_action_name("group_detail")
    def retrieve(self, request, pk=None):
        '''get group details
        :param METHOD: GET
        :param URLPATH: /v1/groups/{group_id}/
        :returns:
            ::

                {
                    'id': GROUP_ID,
                    'groupname': GROUP_NAME,
                    'type': GROUP_TYPE,
                    'status': GROUP_STATUS,
                    'description': GROUP_DESCRIPTION,
                    'created_at': GROUP_CREATE_TIME,
                    'updated_at': GROUP_UPDATE_TIME
                }

        '''
        group_id = pk
        result = get_group_by_id(group_id)
        return json_response(result)

    @policy_protected
    @func_action_name("group_update")
    def update(self, request, pk=None):
        '''update group information
        :param METHOD: PUT
        :param URLPATH: /v1/groups/{group_id}/
        :param dict:
            ::

                {
                    'groupname': GROUP_NAME,
                    'type': GROUP_TYPE,
                    'description': GROUP_DESCRIPTION,
                }

        :returns:
            ::

                {
                    'id': GROUP_ID,
                    'groupname': GROUP_NAME,
                    'updated_at': GROUP_UPDATE_TIME
                }
        '''
        reqparams = get_request_data(request)
        result = group_update(pk, reqparams)
        return json_response(result)

    @policy_protected
    @func_action_name("group_delete")
    def destroy(self, request, pk=None):
        '''delete a existing group
        :param METHOD: DELETE
        :param URLPATH: /v1/groups/{group_id}/
        :returns: {}
        '''
        group_id = pk
        result = group_delete(group_id)
        return json_response(result)
