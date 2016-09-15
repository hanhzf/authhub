# -*- coding: utf-8 -*-
#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#


import logging
import os

LOG = logging.getLogger(__name__)


def read_cached_file(cache, filename, force_reload=False):
    """Read from a file if it has been modified.

    :param force_reload: Whether to reload the file.
    :returns: A tuple with a boolean specifying if the data is fresh
              or not.
    """

    if force_reload:
        delete_cached_file(cache, filename)

    reloaded = False
    mtime = os.path.getmtime(filename)
    cache_info = cache.setdefault(filename, {})

    if not cache_info or mtime > cache_info.get('mtime', 0):
        LOG.debug("Reloading cached file %s", filename)
        with open(filename) as fap:
            cache_info['data'] = fap.read()
        cache_info['mtime'] = mtime
        reloaded = True
    return (reloaded, cache_info['data'])


def delete_cached_file(cache, filename):
    """Delete cached file if present.

    :param filename: filename to delete
    """

    try:
        del cache[filename]
    except KeyError:
        pass
