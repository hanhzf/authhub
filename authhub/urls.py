# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

'''
    This is the main api route for Zen service.
    default api version is v1.
'''

from django.conf.urls import include, url, patterns

urlpatterns = patterns('', url(r'^v1/', include('authhub.apps.v1.urls')),
)
