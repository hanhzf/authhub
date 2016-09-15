# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

import copy
import threading
from sqlalchemy.orm import joinedload

from oslo_db.sqlalchemy import utils as sqlalchemyutils

from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import session as db_session
from authhub.db.models.authmodel import Users, Roles, UserRole, Groups, GroupUser
from commutils.log import log as logging
from commutils.conf.gconf import get_pg_conf
from authhub.common.exception import DBReferenceFailure, DBEntryAleadyExist,\
    DBEntryNotExist
from authhub.common.constant import RESOURCE_USER, RESOURCE_ROLE,\
    RESOURCE_USER_ROLE, RESOURCE_GROUP, RESOURCE_GROUP_USER
from authhub.db.query_filter import process_sort_params, exact_query_filter,\
    logic_query_filter, regex_query_filter, regex_or_query_filter,\
    read_deleted_filter


_ENGINE_FACADE = None
_LOCK = threading.Lock()

LOG = logging.getLogger(__name__)

db_config = get_pg_conf()

RES_MODEL_MAP = {
    RESOURCE_USER: Users,
    RESOURCE_GROUP: Groups,
    RESOURCE_GROUP_USER: GroupUser,
    RESOURCE_ROLE: Roles,
    RESOURCE_USER_ROLE: UserRole
}

def _create_facade(conf):
    '''create database facade
    '''

    sql_connection = 'postgresql://%s:%s@%s:%s/%s' % (db_config['db_user'],
                                                      db_config['db_passwd'],
                                                      db_config['db_host'],
                                                      db_config['db_port'],
                                                      db_config['db_name'])
    return db_session.EngineFacade(
        sql_connection=sql_connection,
        slave_connection=db_config['db_slave_connection'],
        #sqlite_fk=db_config['db_sqlite_fk'],
        #autocommit=db_config['db_autocommit'],
        #expire_on_commit=db_config['db_expire_on_commit'],
        #mysql_sql_mode=db_config['db_mysql_sql_mode'],
        #idle_timeout=db_config['db_idle_timeout'],
        #connection_debug=db_config['db_connection_debug'],
        #max_pool_size=conf.max_pool_size,
        #max_overflow=conf.max_overflow,
        #pool_timeout=conf.pool_timeout,
        #sqlite_synchronous=conf.sqlite_synchronous,
        #connection_trace=conf.connection_trace,
        #max_retries=conf.max_retries,
        #retry_interval=db_config['db_retry_interval']
        )


def _create_facade_lazily():
    global _LOCK, _ENGINE_FACADE
    if _ENGINE_FACADE is None:
        with _LOCK:
            if _ENGINE_FACADE is None:
                _ENGINE_FACADE = _create_facade(db_config)
    return _ENGINE_FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(autocommit=True, expire_on_commit=False):
    facade = _create_facade_lazily()
    return facade.get_session(autocommit=autocommit,
                              expire_on_commit=expire_on_commit)


def model_query(model,
                session=None,
                args=None,
                use_slave=False,
                read_deleted=None):
    """Query helper that accounts for context's `read_deleted` field.

    :param model:       Model to query. Must be a subclass of ModelBase.
    :param args:        Arguments to query. If None - model is used.
    :param session:     If present, the session to use.
    :param use_slave:   If true, use a slave connection to the DB if creating a
                        session.
    :param read_deleted: If not None, overrides context's read_deleted field.
                        Permitted values are 'no', which does not return
                        deleted values; 'only', which only returns deleted
                        values; and 'yes', which does not filter deleted
                        values.
    """

    if session is None:
        session = get_session(use_slave=use_slave)

    if read_deleted is None:
        read_deleted = 'no'

    query_kwargs = {}
    if 'no' == read_deleted:
        query_kwargs['deleted'] = False
    elif 'only' == read_deleted:
        query_kwargs['deleted'] = True
    elif 'yes' == read_deleted:
        pass
    else:
        raise ValueError("Unrecognized read_deleted value '%s'"
                         % read_deleted)

    query = sqlalchemyutils.model_query(model, session, args, **query_kwargs)

    return query


def get_by_all_filters(resource,
                       filters,
                       exact_match_filter_names=[],
                       logic_match_filter_names=[],
                       sort_keys=None,
                       sort_dirs=None,
                       columns_to_join=[],
                       limit=None,
                       pageno=1,
                       marker=None,
                       use_slave=False,
                       read_deleted = None,
                       regex_or_match_filter_names=[],
                       only_check_count=False,
                       distinct_column=None):

    query_prefix = get_queryobj_by_all_filters(resource,
                                               filters,
                                               exact_match_filter_names,
                                               logic_match_filter_names,
                                               sort_keys,
                                               sort_dirs,
                                               columns_to_join,
                                               limit,
                                               pageno,
                                               marker,
                                               use_slave,
                                               read_deleted,
                                               regex_or_match_filter_names,
                                               distinct_column)
    if only_check_count:
        return query_prefix.count()
    else:
        return query_prefix.all()


def get_queryobj_by_all_filters(resource,
                                filters,
                                exact_match_filter_names=[],
                                logic_match_filter_names=[],
                                sort_keys=None,
                                sort_dirs=None,
                                columns_to_join=[],
                                limit=None,
                                pageno=1,
                                marker=None,
                                use_slave=False,
                                read_deleted = None,
                                regex_or_match_filter_names=[],
                                distinct_column=None):

    dbmodel = RES_MODEL_MAP[resource]
    # Filter empty parameter
    for search_key in copy.deepcopy(filters):
        if not filters[search_key] and filters[search_key] != 0:
            del filters[search_key]
    # If the limit is 0 there is no point in even going
    # to the database since nothing is going to be returned anyway.
    if limit == 0:
        return []

    # Make a copy of the filters dictionary to use going forward, as we'll
    # be modifying it and we shouldn't affect the caller's use of it.
    filters = filters.copy()

    sort_keys, sort_dirs = process_sort_params(sort_keys,
                                                      sort_dirs,
                                                      default_dir='desc')
    
    session = get_session()
    # SELECT DISTINCT [COLUMN] FROM [TABLE] WHERE [COLOMN] = [VALUE]
    if distinct_column:
        query_prefix = session.query(dbmodel).distinct(distinct_column).order_by(distinct_column)
    else:
        query_prefix = session.query(dbmodel)
    for column in columns_to_join:
        query_prefix = query_prefix.options(joinedload(column))

    # exact the query
    query_prefix = exact_query_filter(dbmodel, query_prefix,
                                filters, exact_match_filter_names)

    #logic filter
    query_prefix = logic_query_filter(dbmodel, query_prefix,
                                filters, logic_match_filter_names)

    # regex filter
    query_prefix = regex_query_filter(dbmodel, query_prefix, filters)

    # regex filter with or logic
    query_prefix = regex_or_query_filter(dbmodel, query_prefix, regex_or_match_filter_names)


    # whether read deleted value or not
    if read_deleted is None:
        read_deleted = 'no'

    deleted_filters = {}
    if 'no' == read_deleted:
        deleted_filters['deleted'] = False
    elif 'only' == read_deleted:
        deleted_filters['deleted'] = True
    elif 'yes' == read_deleted:
        pass
    else:
        raise ValueError("Unrecognized read_deleted value '%s'"
                         % read_deleted)

    query_prefix = read_deleted_filter(dbmodel, query_prefix, deleted_filters)

    try:
        query_prefix = sqlalchemyutils.paginate_query(query_prefix,
                               dbmodel, limit,
                               sort_keys,
                               marker=marker,
                               sort_dirs=sort_dirs)
    except db_exc.InvalidSortKey, e:
        LOG.exception(e)
        raise Exception.InvalidSortKey()

    return query_prefix



# ----------------------------------------------------------------------------
#    add common database operation for all resources here
# ----------------------------------------------------------------------------
def resource_create(resource_name, values):
    '''insert a resource row into database
    '''
    session = get_session()
    resource_dbmodel = get_dbmodel_for_resource(resource_name)
    if resource_dbmodel is None:
        return None
    resoruce_db_ref = resource_dbmodel()
    resoruce_db_ref.update(values)

    try:
        resoruce_db_ref.save(session)
    except db_exc.DBDuplicateEntry:
        errmsg = ("%s already exists" % (resource_name))
        raise DBEntryAleadyExist(message=errmsg)
    return resoruce_db_ref


def get_resource_by_exact_filter(resource_name, exact_filter, session= None, use_slave=False, join_column=''):
    '''get resource ref according to resource id
    '''
    session = get_session()
    resource_dbmodel = get_dbmodel_for_resource(resource_name)
    query = model_query(resource_dbmodel, session=session,
                        use_slave=use_slave).filter_by(**exact_filter)
    if(join_column):
        query = query.options(joinedload(join_column)) 
    result = query.first()

    if result is None:
        raise DBEntryNotExist(u'%s does not exist' % resource_name)

    return result


def get_resources_by_exact_filter(context, resource_name, exact_filter, session= None, use_slave=False, join_column=''):
    '''note: this function returns a list of resources
    '''
    session = get_session()
    resource_dbmodel = get_dbmodel_for_resource(resource_name)
    query = model_query(context, resource_dbmodel, session=session,
                        use_slave=use_slave).filter_by(**exact_filter)
    if('' != join_column):
        query = query.options(joinedload(join_column)) 
    result = query.all()
    return result


def resource_update(resource_name, resource_id, values):
    '''update a resource
    '''
    session = get_session()
    with session.begin():
        resource_ref = get_resource_by_exact_filter(resource_name, {'id': resource_id}, session=session)
        # check whether resource_ref is None
        resource_ref.update(values)
        resource_ref.save()
    return resource_ref


def resource_delete(resource_name, resource_id, soft_del=True):
    '''delete a resource
    '''
    resource_dbmodel = get_dbmodel_for_resource(resource_name)
    if resource_dbmodel:
        result = 0
        session = get_session()
        with session.begin():
            try:
                if soft_del:
                    result = model_query(resource_dbmodel,
                                         session).\
                                         filter_by(id=resource_id).\
                                         soft_delete(synchronize_session=False)
                else:
                    result = model_query(resource_dbmodel,
                                         session).\
                                         filter_by(id=resource_id).\
                                         delete(synchronize_session=False)
            except db_exc.DBReferenceError, e:
                LOG.exception(e)
                raise DBReferenceFailure()

            if result == 0:
                raise DBEntryNotExist(message='%s does not exist' % resource_name) 


def resource_delete_by_exact_filter(resource_name, exact_filter, soft_del=True):
    '''
        delete a resource
    '''
    resource_dbmodel = get_dbmodel_for_resource(resource_name)
    if resource_dbmodel:
        result = 0
        session = get_session()
        with session.begin():
            try:
                if soft_del:
                    result = model_query(resource_dbmodel,
                                         session).\
                                         filter_by(**exact_filter).\
                                         soft_delete(synchronize_session=False)
                else:
                    result = model_query(resource_dbmodel,
                                         session).\
                                         filter_by(**exact_filter).\
                                         delete(synchronize_session=False)
            except db_exc.DBReferenceError, e:
                LOG.exception(e)
                raise DBReferenceFailure()

            if result == 0:
                raise DBEntryNotExist(message=u'%s does not exist' % resource_name) 


def get_dbmodel_for_resource(resource_name):
    '''
        get dbmodel for resource according to resource name
    '''
    resource_dbmodel = RES_MODEL_MAP.get(resource_name)
    if not resource_dbmodel:
        LOG.error('could not find dbmodel for resource %s' % resource_name)
        return None
    return resource_dbmodel


def db_get_user_role_list(user_id):
    ret = get_by_all_filters(RESOURCE_USER_ROLE,
                             {'user_id': user_id},
                             sort_keys= ['created_at'],
                             exact_match_filter_names=['user_id'],
                             columns_to_join=['role'])
    return ret


def db_get_group_user_list(group_id):
    ret = get_by_all_filters(RESOURCE_GROUP_USER,
                             {'group_id': group_id},
                             sort_keys= ['created_at'],
                             exact_match_filter_names=['group_id'],
                             columns_to_join=['user'])
    return ret
