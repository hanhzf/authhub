# -*- coding: utf-8 -*-
#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

from yaml import load
from yaml import Loader
from commutils.log import log as logging
LOG = logging.getLogger(__name__)


def yaml_load(filename):
    '''load yaml file and return yaml object
    '''
    with open(filename, 'r') as stream:
        try:
            return load(stream, Loader=Loader)
        except Exception, e:
            LOG.error("failed to load <%s> with error %s" % (filename, e))
            return None
