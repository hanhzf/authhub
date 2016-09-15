# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

from authhub.db import model_base
from authhub.db.models import authmodel

def get_metadata():
    return model_base.BASE.metadata
