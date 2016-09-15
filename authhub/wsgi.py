# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#


"""
WSGI config for authhub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys

# set python path
path_to_add = (
    '/opt/zen/authhub', #  need add a ',' at the end if only 1 element in tuple
    )

for path in path_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

from django.core.wsgi import get_wsgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = "authhub.settings"

application = get_wsgi_application()

from commutils.log import log as logging
from commutils.conf.gconf import get_log_conf
logging.setup(get_log_conf(), "authhub")
