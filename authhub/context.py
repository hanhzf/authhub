# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

import datetime
from commutils.log import log as logging
from commutils.cache import mcmodel
from authhub.db import api as db_api
from commutils.conf.gconf import get_memcahce_conf
from authhub.policy.policy import ZenPolicy
LOG = logging.getLogger(__name__)


class ContextBase(object):
    """Security context and request information.

    Represents the user taking a given action within the system.

    """

    def __init__(self, user_id=None, auth_token=None, roles=None, timestamp=None, **kwargs):
        """Object initialization.
        """

        self.user_id = user_id
        self.auth_token = auth_token

        if not timestamp:
            timestamp = datetime.datetime.utcnow()
        self.timestamp = timestamp
        self.roles = roles or []
        self.read_deleted = 'no'
        # check security
        #if self.is_admin is None:
        #    self.is_admin = policy.check_is_admin(self)


    def to_dict(self):
        context = {}
        context.update({
            'user_id': self.user_id,
            'roles': self.roles,
            'timestamp': str(self.timestamp),
        })
        return context

    @classmethod
    def from_dict(cls, values):
        return cls(**values)


class Context(ContextBase):
    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)
        self._session = None
        self.policyChecker = ZenPolicy()
        self.memclient = mcmodel.McModel(get_memcahce_conf())

    @property
    def session(self):
        if self._session is None:
            self._session = db_api.get_session()
        return self._session


g_context = Context()
