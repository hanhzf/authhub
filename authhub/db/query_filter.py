from sqlalchemy import or_
from oslo_db import exception


LOGIN_QUERY_OPERATOR = {
    'NOT_IN': 'NOT_IN',
    'OPERATOR_GE': '>=',
    'OPERATOR_GT':  '>',
    'OPERATOR_LE':  '<=',
    'OPERATOR_LT':  '<',
    'OPERATOR_NE':  '!=',
    'OPERATOR_BETWEEN': 'between'
}


def _get_regexp_op_for_connection(dbtype):
    regexp_op_map = {
        'postgresql': '~',
        'mysql': 'REGEXP',
        'sqlite': 'REGEXP'
    }
    return regexp_op_map.get(dbtype, 'LIKE')


def exact_query_filter(model, query, filters, legal_keys):
    """Applies exact match filtering to an model query.

    Returns the updated query.  Modifies filters argument to remove
    filters consumed.

    :param query: query to apply filters to
    :param filters: dictionary of filters; values that are lists,
                    tuples, sets, or frozensets cause an 'IN' test to
                    be performed, while exact matching ('==' operator)
                    is used for other values
    :param legal_keys: list of keys to apply exact filtering to
    Note: take care that filters is popped here, so it's value will
        be changed in this function
    """

    filter_dict = {}

    # Walk through all the keys
    for key in legal_keys:
        # Skip ones we're not filtering on
        if key not in filters:
            continue

        # OK, filtering on this key; what value do we search for?
        value = filters.pop(key)

        if isinstance(value, (list, tuple, set, frozenset)):
            # Looking for values in a list; apply to query directly
            column_attr = getattr(model, key)
            if value[0] == LOGIN_QUERY_OPERATOR['NOT_IN']:
                query = query.filter(~column_attr.in_(value))
            else:
                query = query.filter(column_attr.in_(value))
        else:
            # OK, simple exact match; save for later
            filter_dict[key] = value

    # Apply simple exact matches
    if filter_dict:
        query = query.filter_by(**filter_dict)

    return query


def regex_query_filter(model, query, filters):
    """Applies regular expression filtering to an model query.

    Returns the updated query.

    :param query: query to apply filters to
    :param filters: dictionary of filters with regex values
    """

    db_regexp_op = _get_regexp_op_for_connection('postgresql')
    for filter_name in filters:
        try:
            column_attr = getattr(model, filter_name)
        except AttributeError:
            continue
        if db_regexp_op == 'LIKE':
            query = query.filter(column_attr.op(db_regexp_op)(
                                 '%' + unicode(filters[filter_name]) + '%'))
        else:
            query = query.filter(column_attr.op(db_regexp_op)(
                                 unicode(filters[filter_name])))
    return query


def regex_or_query_filter(model, query, filters):
    """Applies or (rather than and) regular expression filtering to an model query.

    Returns the updated query.

    :param query: query to apply filters to
    :param filters: dictionary of filters with regex values
    """
    regex_or_filters = []

    db_regexp_op = _get_regexp_op_for_connection('postgresql')
    for filter_name in filters:
        try:
            column_attr = getattr(model, filter_name)
        except AttributeError:
            continue
        if db_regexp_op == 'LIKE':
            qstr = '%' + unicode(filters[filter_name]) + '%'
            regex_or_filters.append(column_attr.op(db_regexp_op)(qstr))
        else:
            qstr = unicode(filters[filter_name])
            regex_or_filters.append(column_attr.op(db_regexp_op)(qstr))

    query = query.filter(or_(*regex_or_filters))
    return query


def logic_query_filter(model, query, filters, legal_keys):
    """Applies logic filtering to an model query.

    Returns the updated query.  Modifies filters argument to remove
    filters consumed.

    :param query: query to apply filters to
    :param filters: dictionary of filters; values that are lists,
                    tuples, sets, or frozensets cause an 'IN' test to
                    be performed, while exact matching ('==' operator)
                    is used for other values
    :param legal_keys: list of keys to apply exact filtering to
    Note: take care that filters is popped here, so it's value will
        be changed in this function
    """
    # Walk through all the keys
    for key in legal_keys:
        # Skip ones we're not filtering on
        if key not in filters:
            continue

        # OK, filtering on this key; what value do we search for?
        value = filters.pop(key)

        if isinstance(value, (list, tuple, set, frozenset)):
            # Looking for values in a list; apply to query directly
            column_attr = getattr(model, key)
            if value[0] == LOGIN_QUERY_OPERATOR['OPERATOR_GE']:
                query = query.filter(column_attr >= value[1])
            elif value[0] == LOGIN_QUERY_OPERATOR['OPERATOR_GT']:
                query = query.filter(column_attr > value[1])
            elif value[0] == LOGIN_QUERY_OPERATOR['OPERATOR_LE']:
                query = query.filter(column_attr <= value[1])
            elif value[0] == LOGIN_QUERY_OPERATOR['OPERATOR_LT']:
                query = query.filter(column_attr < value[1])
            elif value[0] == LOGIN_QUERY_OPERATOR['OPERATOR_NE']:
                query = query.filter(column_attr != value[1])
            elif value[0] == LOGIN_QUERY_OPERATOR['OPERATOR_BETWEEN']:
                query = query.filter(column_attr.between(value[1], value[2]))

    return query


def read_deleted_filter(db_model, query, deleted_filters):
    deleted = deleted_filters['deleted']
    if 'deleted' not in db_model.__table__.columns:
        raise ValueError(("There is no `deleted` column in `%s` table. "
                          "Project doesn't use soft-deleted feature.")
                         % db_model.__name__)

    default_deleted_value = db_model.__table__.c.deleted.default.arg
    if deleted:
        query = query.filter(db_model.deleted != default_deleted_value)
    else:
        query = query.filter(db_model.deleted == default_deleted_value)
    return query


def process_sort_params(sort_keys, sort_dirs,
                        default_keys=['created_at'],
                        default_dir='asc'):
    """Process the sort parameters to include default keys.

    Creates a list of sort keys and a list of sort directions. Adds the default
    keys to the end of the list if they are not already included.

    When adding the default keys to the sort keys list, the associated
    direction is:
    1) The first element in the 'sort_dirs' list (if specified), else
    2) 'default_dir' value (Note that 'asc' is the default value since this is
    the default in sqlalchemy.utils.paginate_query)

    :param sort_keys: List of sort keys to include in the processed list
    :param sort_dirs: List of sort directions to include in the processed list
    :param default_keys: List of sort keys that need to be included in the
                         processed list, they are added at the end of the list
                         if not already specified.
    :param default_dir: Sort direction associated with each of the default
                        keys that are not supplied, used when they are added
                        to the processed list
    :returns: list of sort keys, list of sort directions
    :raise exception.InvalidInput: If more sort directions than sort keys
                                   are specified or if an invalid sort
                                   direction is specified
    """
    # Determine direction to use for when adding default keys
    if sort_dirs and len(sort_dirs) != 0:
        default_dir_value = sort_dirs[0]
    else:
        default_dir_value = default_dir

    # Create list of keys (do not modify the input list)
    if sort_keys:
        result_keys = list(sort_keys)
    else:
        result_keys = []

    # If a list of directions is not provided, use the default sort direction
    # for all provided keys
    if sort_dirs:
        result_dirs = []
        # Verify sort direction
        for sort_dir in sort_dirs:
            if sort_dir not in ('asc', 'desc'):
                msg = "Unknown sort direction, must be 'desc' or 'asc'"
                raise exception.InvalidInput(error_message=msg)
            result_dirs.append(sort_dir)
    else:
        result_dirs = [default_dir_value for _sort_key in result_keys]

    # Ensure that the key and direction length match
    while len(result_dirs) < len(result_keys):
        result_dirs.append(default_dir_value)
    # Unless more direction are specified, which is an error
    if len(result_dirs) > len(result_keys):
        msg = "Sort direction size exceeds sort key size"
        raise exception.InvalidInput(error_message=msg)

    # Ensure defaults are included
    for key in default_keys:
        if key not in result_keys:
            result_keys.append(key)
            result_dirs.append(default_dir_value)

    return result_keys, result_dirs
