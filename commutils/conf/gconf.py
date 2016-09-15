# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

import threading
import os
import time
from commutils.log import log as logging
from contextlib import contextmanager
from commutils.utils.yamlutil import yaml_load
from commutils.utils.secure import unobfuscate_str

LOG = logging.getLogger(__name__)


class ConfLoader(threading.Thread):
    '''configuration file loader that will load configuration file
        automatically per second
    '''
    def __init__(self):
        threading.Thread.__init__(self)
        self.rlock = threading.RLock()
        self.conf_path = '/opt/zen/conf/'

        self.config = {
            'authhub': {'mtime': None, 'data': None}
        }

    def run(self):
        while True:
            try:
                for conf_name in self.config.keys():
                    self._load_conf(conf_name)
                time.sleep(1)
            except Exception, e:
                LOG.error("failed to update config file with error: %s" % e)
                time.sleep(1)

    def _load_conf(self, component):
        '''load configuration file for component
        '''
        with self._read_lock():
            conf_file = os.path.join(self.conf_path, component) + '.yml'
            if not os.path.exists(conf_file):
                LOG.error("<%s> config <%s> does not exist"
                          % (component, conf_file))
                return

            mtime = os.path.getmtime(conf_file)
            cfginfo = self.config.setdefault(component, {})
            if not cfginfo or mtime > cfginfo.get('mtime', 0):
                cfginfo['data'] = yaml_load(conf_file)
                cfginfo['mtime'] = mtime

    def get_conf(self, component="authhub"):
        ''' get component's configuration file
        in case the thread does not not get configuration when our program
        runs, we should can this method first in our app.
        '''
        if not self.config[component].get('data'):
            self._load_conf(component)
        return self.config[component].get('data')

    @contextmanager
    def _read_lock(self):
        self.rlock.acquire()
        try:
            yield
        except Exception, e:
            LOG.info("yeild failed with error: %s" % e)
        self.rlock.release()


g_conf_manager = None


def get_global_conf_manager():
    '''get global configuration manager'''
    global g_conf_manager
    if not g_conf_manager:
        g_conf_manager = ConfLoader()
        g_conf_manager.setDaemon(True)
        g_conf_manager.start()
    g_conf_manager.get_conf()
    return g_conf_manager


def get_log_conf():
    '''get log configuration
    '''
    gconf = get_global_conf_manager().get_conf()
    logcfg = gconf.get('log', {})
    return {
        'debug': logcfg.get('debug', False),
        'verbose': logcfg.get('verbose', False),
        'log_dir': logcfg.get('log_dir', '/opt/zen/logs/'),
        'log_date_format': logcfg.get('log_date_format', '"%Y-%m-%d %H:%M:%S'),
        'log_format': logcfg.get('log_format', 
                                 '%(asctime)s.%(msecs)03d %(thread)d %(levelname)s '
                                 '%(name)s [-] %(message)s [-] '
                                 '%(module)s %(funcName)s:%(lineno)d'),
        'logging_debug_format': logcfg.get('logging_debug_format',
                                           '%(funcName)s %(pathname)s:%(lineno)d'),
        'use_stderr': logcfg.get('use_stderr', False),
        'use-syslog': logcfg.get('use-syslog', False)
    }


def get_memcahce_conf():
    '''get memcache sever address
    '''
    gconf = get_global_conf_manager().get_conf()
    try:
        pgcfg = gconf['memcache']
        if not isinstance(pgcfg, list):
            raise Exception("memcache should be configured as server list")
        return pgcfg
    except Exception, e:
        LOG.error("failed to get memcache config with error %s" % e)
        raise e


def get_pg_conf():
    '''get postgresql configuration
    '''
    gconf = get_global_conf_manager().get_conf()
    try:
        pgcfg = gconf['postgres']
        return {
            'db_name': 'authhub',
            'db_user': 'authhubadm',
            'db_passwd': unobfuscate_str(pgcfg['passwd']),
            'db_host': pgcfg['host'],
            'db_port': 5432,
            'db_slave_connection': False,
            'db_sqlite_fk': False,
            'db_autocommit': True,
            'db_expire_on_commit': False,
            'db_mysql_sql_mode': 'TRADITIONAL',
            'db_idle_timeout': 3600,
            'db_connection_debug': 0,
            'db_retry_interval': 20
        }

    except Exception, e:
        LOG.error("failed to get postgres config with error %s" % e)
        raise e


def get_common_conf():
    '''get common configuration
    '''
    gconf = get_global_conf_manager().get_conf()
    try:
        cmnfg = gconf['common']
        return cmnfg
    except Exception, e:
        LOG.error("failed to get common config with error %s" % e)
        raise e
