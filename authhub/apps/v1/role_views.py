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
from authhub.resources.role import role_create, role_list,\
    role_delete, get_role_by_id, role_update
from authhub.policy.policy_tools import policy_protected

LOG = logging.getLogger(__name__)


class RoleViewSet(viewsets.ViewSet):

    @policy_protected
    @func_action_name("role_list")
    def list(self, request):
        '''list of all existing roles
        :param METHOD: GET
        :param URLPATH: /v1/roles/

        :returns list:
            ::

                [
                    {
                        'id': ROLE_ID,
                        'name': ROLE_NAME,
                        'created_at': ROLE_CREATE_TIME
                    },
                    {
                        'id': ROLE_ID,
                        'name': ROLE_NAME,
                        'created_at': ROLE_CREATE_TIME
                    },
                    ......
                ]

        '''
        reqparams = get_request_data(request)
        result = role_list(reqparams)
        return json_response(result)

    @policy_protected
    @func_action_name("role_create")
    def create(self, request):
        '''create new roles
        :param METHOD: POST
        :param URLPATH: /v1/roles/
        :param dict:
            ::

                {
                    'name': ROLE_NAME,
                    'description': ROLE_DESCRIPTION
                }

        :returns:
            ::

                {
                    'id': ROLE_ID,
                    'name': ROLE_NAME
                }

        '''
        reqparams = get_request_data(request)
        result = role_create(reqparams)
        return json_response(result)

    @policy_protected
    @func_action_name("role_detail")
    def retrieve(self, request, pk=None):
        '''get role details
        :param METHOD: GET
        :param URLPATH: /v1/roles/{role_id}/
        :returns:
            ::

                {
                    'id': ROLE_ID,
                    'name': ROLE_NAME,
                    'description': ROLE_DESCRIPTION,
                    'created_at': ROLE_CREATE_TIME,
                    'updated_at': ROLE_UPDATE_TIME
                }

        '''
        role_id = pk
        result = get_role_by_id(role_id)
        return json_response(result)

    @policy_protected
    @func_action_name("role_update")
    def update(self, request, pk=None):
        '''update role information
        :param METHOD: PUT
        :param URLPATH: /v1/roles/{role_id}/
        :param dict:
            ::

                {
                    'description': ROLE_DESCRIPTION,
                }

        :returns:
            ::

                {
                    'id': ROLE_ID,
                    'name': ROLE_NAME,
                    'updated_at': ROLE_UPDATE_TIME
                }
        '''
        reqparams = get_request_data(request)
        result = role_update(pk, reqparams)
        return json_response(result)

    @policy_protected
    @func_action_name("role_delete")
    def destroy(self, request, pk=None):
        '''delete a existing role
        :param METHOD: DELETE
        :param URLPATH: /v1/roles/{role_id}/
        :returns: {}
        '''
        role_id = pk
        result = role_delete(role_id)
        return json_response(result)
