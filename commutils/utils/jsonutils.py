'''
JSON related utilities.

This module provides a few things:

#. A handy function for getting an object down to something that can be
   JSON serialized.  See :func:`.to_primitive`.
#. Wrappers around :func:`.loads` and :func:`.dumps`. The :func:`.dumps`
   wrapper will automatically use :func:`.to_primitive` for you if needed.
#. This sets up ``anyjson`` to use the :func:`.loads` and :func:`.dumps`
   wrappers if ``anyjson`` is available.
'''


import codecs
import datetime
import functools
import inspect
import itertools
import sys
import uuid

from commutils.utils import encodeutils
from commutils.utils import importutils
from commutils.utils import timeutils
import six

is_simplejson = False
if sys.version_info < (2, 7):
    # On Python <= 2.6, json module is not C boosted, so try to use
    # simplejson module if available
    try:
        import simplejson as json
        # NOTE(mriedem): Make sure we have a new enough version of simplejson
        # to support the namedobject_as_tuple argument. This can be removed
        # in the Kilo release when python 2.6 support is dropped.
        if 'namedtuple_as_object' in inspect.getargspec(json.dumps).args:
            is_simplejson = True
        else:
            import json
    except ImportError:
        import json
else:
    import json


netaddr = importutils.try_import("netaddr")


_simple_types = (six.string_types + six.integer_types + (type(None),
                                                         bool, float))


def to_primitive(value, convert_instances=False, convert_datetime=True,
                 level=0, max_depth=3):
    """Convert a complex object into primitives.

    Handy for JSON serialization. We can optionally handle instances,
    but since this is a recursive function, we could have cyclical
    data structures.

    To handle cyclical data structures we could track the actual objects
    visited in a set, but not all objects are hashable. Instead we just
    track the depth of the object inspections and don't go too deep.

    Therefore, ``convert_instances=True`` is lossy ... be aware.
    """

    if isinstance(value, _simple_types):
        return value

    # handle invalid time format
    try:
        if isinstance(value, datetime.datetime):
            if convert_datetime:
                return value.strftime(timeutils.PERFECT_TIME_FORMAT)
            else:
                return value

        if isinstance(value, datetime.date):
            if convert_datetime:
                return value.strftime(timeutils.PERFECT_DATE_FORMAT)
            else:
                return value

        # note: pure for activity begin_time and end_time handle
        if isinstance(value, datetime.time):
            if convert_datetime:
                return value.strftime(timeutils.PERFECT_HOUR_MINIUTE_FORMAT)
            else:
                return value
    except Exception:
        return 'INVALID_TIME_FMT'

    if isinstance(value, uuid.UUID):
        return six.text_type(value)

    if netaddr and isinstance(value, netaddr.IPAddress):
        return six.text_type(value)

    # value of itertools.count doesn't get caught by nasty_type_tests
    # and results in infinite loop when list(value) is called.
    if type(value) == itertools.count:
        return six.text_type(value)

    if level > max_depth:
        return '?'

    # The try block may not be necessary after the class check above,
    # but just in case ...
    try:
        recursive = functools.partial(to_primitive,
                                      convert_instances=convert_instances,
                                      convert_datetime=convert_datetime,
                                      level=level,
                                      max_depth=max_depth)
        if isinstance(value, dict):
            return dict((recursive(k), recursive(v))
                        for k, v in six.iteritems(value))
        # comment complicated data structures
        # elif hasattr(value, 'iteritems'):
        #     return recursive(dict(value.iteritems()), level=level + 1)
        # elif hasattr(value, '__iter__'):
        #     return list(map(recursive, value))
        # elif convert_instances and hasattr(value, '__dict__'):
        # Likely an instance of something. Watch for cycles.
        # Ignore class member vars.
        #     return recursive(value.__dict__, level=level + 1)
    except TypeError:
        # Class objects are tricky since they may define something like
        # __iter__ defined but it isn't callable as list().
        return six.text_type(value)

    return value


JSONEncoder = json.JSONEncoder
JSONDecoder = json.JSONDecoder


def dumps(obj, default=to_primitive, **kwargs):
    """Serialize ``obj`` to a JSON formatted ``str``.

    :param obj: object to be serialized
    :param default: function that returns a serializable version of an object
    :param kwargs: extra named parameters, please see documentation \
    of `json.dumps <https://docs.python.org/2/library/json.html#basic-usage>`_
    :returns: json formatted string
    """
    if is_simplejson:
        kwargs['namedtuple_as_object'] = False
    return json.dumps(obj, default=default, **kwargs)


def dump(obj, fp, *args, **kwargs):
    """Serialize ``obj`` as a JSON formatted stream to ``fp``

    :param obj: object to be serialized
    :param fp: a ``.write()``-supporting file-like object
    :param default: function that returns a serializable version of an object
    :param args: extra arguments, please see documentation \
    of `json.dump <https://docs.python.org/2/library/json.html#basic-usage>`_
    :param kwargs: extra named parameters, please see documentation \
    of `json.dump <https://docs.python.org/2/library/json.html#basic-usage>`_
    """
    default = kwargs.get('default', to_primitive)
    if is_simplejson:
        kwargs['namedtuple_as_object'] = False
    return json.dump(obj, fp, default=default, *args, **kwargs)


def loads(s, encoding='utf-8', **kwargs):
    """Deserialize ``s`` (a ``str`` or ``unicode`` instance containing a JSON

    :param s: string to deserialize
    :param encoding: encoding used to interpret the string
    :param kwargs: extra named parameters, please see documentation \
    of `json.loads <https://docs.python.org/2/library/json.html#basic-usage>`_
    :returns: python object
    """
    return json.loads(encodeutils.safe_decode(s, encoding), **kwargs)


def load(fp, encoding='utf-8', **kwargs):
    """Deserialize ``fp`` to a Python object.

    :param fp: a ``.read()`` -supporting file-like object
    :param encoding: encoding used to interpret the string
    :param kwargs: extra named parameters, please see documentation \
    of `json.loads <https://docs.python.org/2/library/json.html#basic-usage>`_
    :returns: python object
    """
    return json.load(codecs.getreader(encoding)(fp), **kwargs)


try:
    import anyjson
except ImportError:
    pass
else:
    anyjson._modules.append((__name__, 'dumps', TypeError,
                                       'loads', ValueError, 'load'))
    anyjson.force_implementation(__name__)
