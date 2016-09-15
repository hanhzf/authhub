# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#


"""logging handler.

This module adds to logging functionality by adding the option to specify
a context object when calling the various log methods.  If the context object
is not specified, default formatting is used.

It also allows setting of formatting information through conf.
"""

import logging.handlers
import sys
try:
    import syslog
except ImportError:
    syslog = None
import traceback

from commutils.utils import encodeutils
import six
import os
import errno
from commutils.log.formatters import CEWLogFilter
from commutils.log import handlers

_PY26 = sys.version_info[0:2] == (2, 6)


def safe_mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def _get_log_file_path(conf, project, binary=None):
    logdir = conf.get('log_dir')
    safe_mkdirs(logdir)

    logfile = os.path.join(logdir, '%s.log' % project)
    ret = logfile if logfile else None
    return ret


class BaseLoggerAdapter(logging.LoggerAdapter):

    warn = logging.LoggerAdapter.warning

    @property
    def handlers(self):
        return self.logger.handlers

    def isEnabledFor(self, level):
        if _PY26:
            # This method was added in python 2.7 (and it does the exact
            # same logic, so we need to do the exact same logic so that
            # python 2.6 has this capability as well).
            return self.logger.isEnabledFor(level)
        else:
            return super(BaseLoggerAdapter, self).isEnabledFor(level)


def _ensure_unicode(msg):
    """Do our best to turn the input argument into a unicode object.
    """
    if not isinstance(msg, six.text_type):
        if isinstance(msg, six.binary_type):
            msg = encodeutils.safe_decode(
                msg,
                encoding='utf-8',
                errors='xmlcharrefreplace',
            )
        else:
            msg = six.text_type(msg)
    return msg


class KeywordArgumentAdapter(BaseLoggerAdapter):
    """Logger adapter to add keyword arguments to log record's extra data

    Keywords passed to the log call are added to the "extra"
    dictionary passed to the underlying logger so they are emitted
    with the log message and available to the format string.

    Special keywords:

    extra
      An existing dictionary of extra values to be passed to the
      logger. If present, the dictionary is copied and extended.
    resource

    """

    def process(self, msg, kwargs):
        msg = _ensure_unicode(msg)
        # Make a new extra dictionary combining the values we were
        # given when we were constructed and anything from kwargs.
        extra = {}
        extra.update(self.extra)
        if 'extra' in kwargs:
            extra.update(kwargs.pop('extra'))
        # Move any unknown keyword arguments into the extra
        # dictionary.
        for name in list(kwargs.keys()):
            if name == 'exc_info':
                continue
            extra[name] = kwargs.pop(name)

        extra['extra_keys'] = list(sorted(extra.keys()))
        # Place the updated extra values back into the keyword
        # arguments.
        kwargs['extra'] = extra

        return msg, kwargs


def _create_logging_excepthook(product_name):
    def logging_excepthook(exc_type, value, tb):
        extra = {'exc_info': (exc_type, value, tb)}
        getLogger(product_name).critical(
            "".join(traceback.format_exception_only(exc_type, value)),
            **extra)
    return logging_excepthook


def setup(conf, project, version='unknown'):
    """Setup logging for the current application."""
    _setup_logging_from_conf(conf, project, version)
    sys.excepthook = _create_logging_excepthook(project)


def _find_facility(facility):
    # NOTE(jd): Check the validity of facilities at run time as they differ
    # depending on the OS and Python version being used.
    valid_facilities = [f for f in
                        ["LOG_KERN", "LOG_USER", "LOG_MAIL",
                         "LOG_DAEMON", "LOG_AUTH", "LOG_SYSLOG",
                         "LOG_LPR", "LOG_ARTICLE", "LOG_UUCP",
                         "LOG_CRON", "LOG_AUTHPRIV", "LOG_FTP",
                         "LOG_LOCAL0", "LOG_LOCAL1", "LOG_LOCAL2",
                         "LOG_LOCAL3", "LOG_LOCAL4", "LOG_LOCAL5",
                         "LOG_LOCAL6", "LOG_LOCAL7"]
                        if getattr(syslog, f, None)]

    facility = facility.upper()

    if not facility.startswith("LOG_"):
        facility = "LOG_" + facility

    if facility not in valid_facilities:
        raise TypeError(_('syslog facility must be one of: %s') %
                        ', '.join("'%s'" % fac
                                  for fac in valid_facilities))

    return getattr(syslog, facility)


def _setup_logging_from_conf(conf, project, version):
    log_root = getLogger(None).logger
    for handler in log_root.handlers:
        log_root.removeHandler(handler)

    logpath = _get_log_file_path(conf, project)

    # setup file handler for all levels
    filelog = logging.handlers.RotatingFileHandler(logpath,
                                                   mode='a',
                                                   maxBytes=100000000,
                                                   backupCount=5)
    log_root.addHandler(filelog)

    # setup file handler for critical, error and warning
    errlog = logging.handlers.RotatingFileHandler(logpath+'.cew',
                                                  mode='a',
                                                  maxBytes=100000000,
                                                  backupCount=5)
    log_root.addHandler(errlog)
    log_root.addFilter(CEWLogFilter)

    if conf.get('use_stderr'):
        streamlog = handlers.ColorHandler()
        log_root.addHandler(streamlog)

    if conf.get('use_syslog'):
        global syslog
        if syslog is None:
            raise RuntimeError("syslog is not available on this platform")
        facility = _find_facility(conf.get('syslog_log_facility'))
        # TODO(bogdando) use the format provided by RFCSysLogHandler after
        # existing syslog format deprecation in J
        syslog = handlers.OSSysLogHandler(
            facility=facility,
            use_syslog_rfc_format=conf.get('use_syslog_rfc_format'))
        log_root.addHandler(syslog)

    datefmt = conf.get('log_date_format')
    for handler in log_root.handlers:
        handler.setFormatter(logging.Formatter(fmt=conf.get('log_format'),
                                               datefmt=datefmt))

    if conf.get('debug'):
        log_root.setLevel(logging.DEBUG)
    elif conf.get('verbose'):
        log_root.setLevel(logging.INFO)
    else:
        log_root.setLevel(logging.WARNING)


_loggers = {}


def getLogger(name=None, project='unknown', version='unknown'):
    """Build a logger with the given name.

    :param name: The name for the logger. This is usually the module
                 name, ``__name__``.
    :type name: string
    :param project: The name of the project, to be injected into log
                    messages. For example, ``'nova'``.
    :type project: string
    :param version: The version of the project, to be injected into log
                    messages. For example, ``'2014.2'``.
    :type version: string
    """
    if name not in _loggers:
        _loggers[name] = KeywordArgumentAdapter(logging.getLogger(name),
                                                {'project': project,
                                                 'version': version})
    return _loggers[name]
