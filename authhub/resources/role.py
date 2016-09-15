# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

from authhub.db import api as db_api
from commutils.log import log as logging
from authhub.common.exception import DBEntryNotExist
from commutils.utils.timeutils import strtime_utc_to_local
from authhub.common.constant import RESOURCE_ROLE
from authhub.common.misc import purify_request_params, check_needed_params
LOG = logging.getLogger(__name__)


def role_create(role_info):
    '''create role info
    :param role_info: required role information for registration, dict
    :return: role info
    '''
    check_needed_params(role_info, ['name'])
    purify_request_params(role_info, ['name', 'description'])

    ret = db_api.resource_create(RESOURCE_ROLE, role_info)

    result = {
        'id': ret['id'],
        'name': ret['name']
    }
    return result


def role_list(role_filter):
    '''list all roles
    :returns: selected role info
    '''
    rlist_ret = []
    purify_request_params(role_filter, ['name'])
    exact_match_filter_names = ['name']

    ret = db_api.get_by_all_filters(RESOURCE_ROLE,
                                    role_filter,
                                    exact_match_filter_names = exact_match_filter_names)

    for rinfo in ret:
        uitem = {
            'id': rinfo.id,
            'name': rinfo.name,
            'created_at': strtime_utc_to_local(rinfo.created_at)
        }
        rlist_ret.append(uitem)

    return rlist_ret


def get_role_by_rolename(role_name):
    '''get role detailed info by role_name
    '''
    return _role_detail(role_name, query_type='name')


def get_role_by_id(role_id):
    '''get role detailed info by role_id
    '''
    return _role_detail(role_id)


def _role_detail(query_obj, query_type='id'):
    '''get role detailed information
    :param query_obj str: either id or rolename
    '''
    query_filter = {}
    # we can get role by id or rolename
    if query_type == 'id':
        query_filter = {'id': query_obj}
    elif query_type == 'name':
        query_filter = {'name': query_obj}
    else:
        return None

    try:
        ret = db_api.get_resource_by_exact_filter(RESOURCE_ROLE,
                                                  query_filter)
    except DBEntryNotExist:
        raise DBEntryNotExist('the role you queried does not exist')

    role_info = {
        "id": ret.id,
        "name": ret.name,
        "description": ret.description,
        "created_at": strtime_utc_to_local(ret.created_at),
        "updated_at": strtime_utc_to_local(ret.updated_at)
    }
    return role_info


def role_update(role_id, role_info, valid_params=None):
    '''update role information(description)
    '''
    purify_request_params(role_info, ['description'])
    ret = db_api.resource_update(RESOURCE_ROLE, role_id, role_info)

    result = {
        'id': ret.id,
        'name': ret.name,
        'updated_at': strtime_utc_to_local(ret.updated_at)
    }
    return result


def role_delete(role_id):
    '''delete role
    '''
    db_api.resource_delete(RESOURCE_ROLE, role_id)
