# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

import re
from authhub.db import api as db_api
from commutils.log import log as logging
from authhub.common.exception import DBEntryNotExist, IncorrectUserOrPasswd,\
    DBEntryAleadyExist
from commutils.utils.timeutils import strtime_utc_to_local, utcnow
from authhub.common.exception import InvalidRequestFormat
from commutils.utils.secure import gen_hashed_password, validate_hashed_password
from authhub.common.constant import RESOURCE_USER, RESOURCE_USER_ROLE,\
    USER_TYPE_P2P, USER_TYPE_BANK, USER_TYPE_SUPERVISOR
from authhub.common.misc import purify_request_params, check_needed_params
from authhub.db.api import db_get_user_role_list,\
    resource_delete_by_exact_filter
from authhub.resources.role import get_role_by_rolename
from oslo_db.exception import DBReferenceError
LOG = logging.getLogger(__name__)


def user_create(user_info):
    '''create user resource
    :param user_info: required user information for registration, dict
    :return: user info
    '''
    check_needed_params(user_info, ['username', 'password', 'type'])

    VALID_USER_TYPES = [USER_TYPE_P2P, USER_TYPE_BANK, USER_TYPE_SUPERVISOR]
    if user_info['type'] not in VALID_USER_TYPES:
        raise InvalidRequestFormat('Invalid user type, must be one of %s'
                                   % VALID_USER_TYPES)

    create_params = {
        "username": user_info['username'],
        "password": gen_hashed_password(user_info['password']),
        "type": user_info['type']
    }

    for k in ['email', 'description']:
        if user_info.get(k):
            create_params[k] = user_info[k]

    #passwd_strength_checker().check_passwd_strength(params['passwd'])

    # check username format
    username = create_params['username']

    if len(username) < 4 or len(username) > 20:
        raise InvalidRequestFormat("invalid username format, the length must be between "
                                   "4 and 20")

    if not re.match('^[a-zA-Z][a-zA-Z0-9_]+$', username):
        raise InvalidRequestFormat("invalid username format, the first letter must be "
                                   "character, others can be either digit, character "
                                   "or underline")

    ret = db_api.resource_create(RESOURCE_USER, create_params)

    result = {
        'id': ret['id'],
        'username': ret['username'],
        'type': ret['type'],
        'status': ret['status']
    }
    return result


def user_list(user_filter):
    '''list all users
    :returns: selected user info
    '''
    ulist_ret = []
    purify_request_params(user_filter, ['username', 'role', 'phone', 'email'])
    exact_match_filter_names = ['username', 'role', 'email']

    ret = db_api.get_by_all_filters(RESOURCE_USER,
                                    user_filter,
                                    exact_match_filter_names = exact_match_filter_names)

    for uinfo in ret:
        uitem = {
            'id': uinfo.id,
            'username': uinfo.username,
            'type': uinfo.type,
            'status': uinfo.status,
            'created_at': strtime_utc_to_local(uinfo.created_at)
        }
        ulist_ret.append(uitem)

    return ulist_ret


def get_user_by_username(username):
    '''get user detailed info by username
    '''
    return _user_detail(username, 'username')


def get_user_by_id(user_id):
    '''get user detailed info by user_id
    '''
    return _user_detail(user_id)


def _user_detail(query_obj, query_type='id'):
    '''get user detailed information
    :param query_obj str: either id or username
    '''
    query_filter = {}
    # we can get user by id or username
    if query_type == 'id':
        query_filter = {'id': query_obj}
    elif query_type == 'username':
        query_filter = {'username': query_obj}
    else:
        return None

    try:
        ret = db_api.get_resource_by_exact_filter(RESOURCE_USER,
                                                  query_filter)
    except DBEntryNotExist:
        raise DBEntryNotExist('the user you queried does not exist')

    user_info = {
        "id": ret.id,
        "username": ret.username,
        'type': ret.type,
        "privilege": ret.privilege,
        "phone": ret.phone,
        "email": ret.email,
        "status": ret.status,
        "description": ret.description,
        "last_login_time": strtime_utc_to_local(ret.last_login_time),
        "created_at": strtime_utc_to_local(ret.created_at),
        "updated_at": strtime_utc_to_local(ret.updated_at)
    }

    user_info["role"] = user_role_list(ret.id)
    return user_info


def user_basic_update(user_id, user_info):
    '''update user basic information like phone, email, description
    :param user_id string: id of user
    :param user_info: the part of info user want to update
    :return: {'id': '', 'username': '', 'updated_at': ''}
    '''
    return _user_update(user_id, user_info, ['phone', 'email', 'description'])


def user_role_grant(user_id, rolename):
    '''update user's role and privilege
    '''
    role_info = get_role_by_rolename(rolename)
    role_id = role_info['id']

    grant_params = {
        'user_id': user_id,
        'role_id': role_id
    }

    try:
        ret = db_api.resource_create(RESOURCE_USER_ROLE, grant_params)
    except DBEntryAleadyExist:
        raise DBEntryAleadyExist('role < %s > has already been granted to user %s'
                                 % (rolename, user_id))
    except DBReferenceError:
        raise DBEntryNotExist('role <%s> does not exist' % rolename)

    result = {
        'user_id': ret.user_id,
        'role_id': ret.role_id,
        'created_at': strtime_utc_to_local(ret.created_at)
    }
    return result


def user_role_revoke(user_id, role_id):
    '''update user's role and privilege
    '''
    query_params = {
        'user_id': user_id,
        'role_id': role_id
    }
    resource_delete_by_exact_filter(RESOURCE_USER_ROLE,
                                    query_params,
                                    soft_del=False
                                    )


def user_role_list(user_id):
    '''return user's role list
    '''
    ret = db_get_user_role_list(user_id)
    user_role_list = [ r['role'].name for r in ret]
    return user_role_list


def user_password_update(user_id, user_pass):
    '''update user's password
    '''
    if not user_pass:
        raise InvalidRequestFormat('please input the new password for user')
    # check new password strength
    return _user_update(user_id, {"password": gen_hashed_password(user_pass)})


def user_lastlogin_time_update(user_id):
    '''update user's last login time
    '''
    last_login_time = utcnow()
    return _user_update(user_id, {'last_login_time': last_login_time})


def _user_update(user_id, user_info, valid_params=None):
    '''update user information
    '''
    if valid_params:
        purify_request_params(user_info, valid_params)

    # get valid parameters
    ret = db_api.resource_update(RESOURCE_USER, user_id, user_info)

    result = {
        'id': ret.id,
        'username': ret.username,
        'updated_at': strtime_utc_to_local(ret.updated_at)
    }
    return result


def user_delete(user_id):
    '''delete user
    '''
    db_api.resource_delete(RESOURCE_USER, user_id)


def user_password_validate(user_id, input_password):
    '''check whether user's password is correct
    :param user_id str: id of user
    :param input_password str: the password user input for login
    :return: invalid username or password if user does not
             exist or password incorrect
    '''
    try:
        ret = db_api.get_resource_by_exact_filter(RESOURCE_USER,
                                                  {'id': user_id})
    except DBEntryNotExist:
        raise IncorrectUserOrPasswd()
    user_pass = ret.password
    if not validate_hashed_password(input_password, user_pass):
        raise IncorrectUserOrPasswd()
