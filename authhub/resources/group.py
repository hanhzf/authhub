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
from authhub.common.exception import DBEntryNotExist, DBEntryAleadyExist
from commutils.utils.timeutils import strtime_utc_to_local
from authhub.common.constant import RESOURCE_GROUP, RESOURCE_GROUP_USER
from authhub.common.misc import purify_request_params, check_needed_params
from authhub.db.api import resource_delete_by_exact_filter, db_get_group_user_list
from oslo_db.exception import DBReferenceError
LOG = logging.getLogger(__name__)


def group_create(group_info):
    '''create group info
    :param group_info: required group information for group creation, dict
    :return: group info
    '''
    check_needed_params(group_info, ['groupname', 'type', 'description'])
    purify_request_params(group_info, ['groupname', 'type', 'description'])

    ret = db_api.resource_create(RESOURCE_GROUP, group_info)

    result = {
        'id': ret['id'],
        'groupname': ret['groupname'],
        'created_at': strtime_utc_to_local(ret.created_at)
    }
    return result


def group_list(group_filter):
    '''list all groups
    :returns: selected group info
    '''
    rlist_ret = []
    purify_request_params(group_filter, ['type', 'groupname'])
    exact_match_filter_names = ['type']

    ret = db_api.get_by_all_filters(RESOURCE_GROUP,
                                    group_filter,
                                    exact_match_filter_names = exact_match_filter_names)

    for rinfo in ret:
        gitem = {
            'id': rinfo.id,
            'groupname': rinfo.groupname,
            'created_at': strtime_utc_to_local(rinfo.created_at)
        }
        rlist_ret.append(gitem)

    return rlist_ret


def get_group_by_id(group_id):
    '''get group detailed info by group_id
    '''
    return _group_detail(group_id)


def _group_detail(query_obj, query_type='id'):
    '''get group detailed information
    :param query_obj str: either id or groupname
    '''
    query_filter = {}
    # we can get group by id or groupname
    if query_type == 'id':
        query_filter = {'id': query_obj}
    else:
        return None

    try:
        ret = db_api.get_resource_by_exact_filter(RESOURCE_GROUP,
                                                  query_filter)
    except DBEntryNotExist:
        raise DBEntryNotExist('the group you queried does not exist')

    group_info = {
        "id": ret.id,
        "groupname": ret.groupname,
        "status": ret.status,
        "description": ret.description,
        "created_at": strtime_utc_to_local(ret.created_at),
        "updated_at": strtime_utc_to_local(ret.updated_at)
    }
    return group_info


def group_update(group_id, group_info, valid_params=None):
    '''update group information(description)
    '''
    purify_request_params(group_info, ['groupname', 'type', 'description'])
    ret = db_api.resource_update(RESOURCE_GROUP, group_id, group_info)

    result = {
        'id': ret.id,
        'groupname': ret.groupname,
        'updated_at': strtime_utc_to_local(ret.updated_at)
    }
    return result


def group_delete(group_id):
    '''delete group
    '''
    db_api.resource_delete(RESOURCE_GROUP, group_id)


def group_user_add(group_id, user_id):
    '''add user to group
    '''
    create_param = {
        'group_id': group_id,
        'user_id': user_id
    }

    try:
        ret = db_api.resource_create(RESOURCE_GROUP_USER, create_param)
    except DBEntryAleadyExist:
        raise DBEntryAleadyExist('user < %s > has already been added to group %s'
                                 % (user_id, group_id))
    except DBReferenceError:
        raise DBEntryNotExist('user with id <%s> does not exist' % user_id)

    result = {
        'group_id': ret.group_id,
        'user_id': ret.user_id,
        'created_at': strtime_utc_to_local(ret.created_at)
    }
    return result


def group_user_delete(group_id, user_id):
    '''remove user from group
    '''
    query_params = {
        'group_id': group_id,
        'user_id': user_id
    }
    resource_delete_by_exact_filter(RESOURCE_GROUP_USER,
                                    query_params,
                                    soft_del=False
                                    )


def group_user_list(group_id):
    '''return group's user list
    '''
    ret = db_get_group_user_list(group_id)
    group_user_list = [ {'id': r['user'].id, 'username': r['user'].username} for r in ret]
    return group_user_list
