# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

from sqlalchemy.types import TypeDecorator
import sqlalchemy as sa
from commutils.utils import jsonutils


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string"""

    impl = sa.Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = jsonutils.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = jsonutils.loads(value)
        return value
