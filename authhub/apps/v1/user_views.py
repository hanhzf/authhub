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
from rest_framework.decorators import detail_route
from authhub.common.misc import json_response, get_request_data,\
    func_action_name
from authhub.resources.user import user_create, user_list,\
    user_delete, user_basic_update, user_password_update, \
    get_user_by_id
from authhub.policy.policy_tools import policy_protected

LOG = logging.getLogger(__name__)


class UserViewSet(viewsets.ViewSet):

    @policy_protected
    @func_action_name("user_list")
    def list(self, request):
        '''list of all existing users
        :param METHOD: GET
        :param URLPATH: /v1/users/
        :return list:
            ::

                [
                    {
                        "id": USER_ID,
                        "username": USER_NAME,
                        "type": USER_TYPE,
                        "status": USER_STATUS,
                        "created_at": USER_CREATED_TIME
                    },
                    {
                        "id": USER_ID,
                        "username": USER_NAME,
                        "type": USER_TYPE,
                        "status": USER_STATUS,
                        "created_at": USER_CREATED_TIME
                    },
                    ......
                ]

        '''
        reqparams = get_request_data(request)
        result = user_list(reqparams)
        return json_response(result)

    @policy_protected
    @func_action_name("user_create")
    def create(self, request):
        '''create new users
        :param METHOD: POST
        :param URLPATH: /v1/users/
        :param dict:
            ::
    
                {
                    'username': USER_NAME,
                    'password': PASSWORD,
                    'type': USER_TYPE,
                    'email': USER_EMAIL,
                    'description': USER_DESCRIPTION
                }

        :return:
            ::

                {
                    "id": USER_ID,
                    "username": USER_NAME,
                    "type": USER_TYPE,
                    "status": USER_STATUS
                }

        '''
        reqparams = get_request_data(request)

        #if params.get('privilege'):
        #    params['privilege'] = int(params['privilege'])
    
        #if params['role'] not in [ROLE_ORG_ADMIN, ROLE_GOV_ADMIN, ROLE_DONATOR_ADMIN, ROLE_SUPER_ADMIN]:
        #    raise InvalidRequestFormat(u'管理员角色不正确，必须为 [%s, %s, %s] 之一'
        #                               % (ROLE_ORG_ADMIN, ROLE_GOV_ADMIN, ROLE_DONATOR_ADMIN))
    
        #operator = user_detail(session_check(request['sid'], app_type)['uid'])
        result = user_create(reqparams)
        #return result

        return json_response(result)

    @policy_protected
    @func_action_name("user_detail")
    def retrieve(self, request, pk=None):
        '''get user details
        :param METHOD: GET
        :param URLPATH: /v1/users/{user_id}/

        :return:
            ::

                {
                    "id": USER_ID,
                    "username": USER_NAME,
                    "type": USER_TYPE,
                    "status": USER_STATUS,
                    "role": USER_ROLE_LIST,
                    "phone": USER_PHONE,
                    "email": USER_EMAIL,
                    "description": USER_DESCRIPTION,
                    "last_login_time": USER_LAST_LOGIN_TIME
                    "created_at": USER_CREATE_TIME,
                    "updated_at": USER_UPDATE_TIME
                }

        '''
        user_id = pk
        result = get_user_by_id(user_id)
        return json_response(result)

    @policy_protected
    @func_action_name("user_update")
    def update(self, request, pk=None):
        '''update user information
        :param METHOD: PUT
        :param URLPATH: /v1/users/{user_id}/
        :param dict:
            ::
    
                {
                    'email': USER_EMAIL,
                    'description': USER_DESCRIPTION
                }

        :return:
            ::

                {
                    "id": USER_ID,
                    "username": USER_NAME,
                    "updated_at": USER_UPDATE_TIME
                }

        '''
        reqparams = get_request_data(request)
        result = user_basic_update(pk, reqparams)
        return json_response(result)

    @policy_protected
    @func_action_name("user_reset_password")
    @detail_route(methods=['put'])
    def reset_password(self, request, pk=None):
        '''update user password
        :param METHOD: PUT
        :param URLPATH: /v1/users/{user_id}/
        :param dict: {'password': NEW_PASSWORD}
        :param dict:
            ::
    
                {
                    'password': PASSWORD
                }

        :return:
            ::

                {
                    "id": USER_ID,
                    "username": USER_NAME,
                    "updated_at": USER_UPDATE_TIME
                }

        '''
        # check permission
        reqparams = get_request_data(request)
        user_id = pk
        result = user_password_update(user_id, reqparams.get('password'))
        return json_response(result)

    @policy_protected
    @func_action_name("user_delete")
    def destroy(self, request, pk=None):
        '''delete existing user
        :param METHOD: DELETE
        :param URLPATH: /v1/users/{user_id}/

        :return: {}

        '''
        user_id = pk
        result = user_delete(user_id)
        return json_response(result)
