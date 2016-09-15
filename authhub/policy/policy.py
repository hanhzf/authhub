# -*- coding: utf-8 -*-
#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

from commutils.log import log as logging
from commutils.utils import filecache as _cache_handler
from commutils.utils import jsonutils
from authhub.common import exception as apiExc
import os


LOG = logging.getLogger(__name__)


class ZenPolicy(object):
    """Responsible for loading and enforcing rules.
    """

    def __init__(self, policy_file=None):

        self.policy_file = policy_file or 'policy.json'
        self._file_cache = {}
        self.rules = {}
        self.policy_path = ''

    def load_rules(self, force_reload=False):
        """Loads policy rules from policy configuration file
        """

        if not self.policy_path:
            self.policy_path = self._get_policy_path()

        self._load_policy_file(self.policy_path, force_reload)

    def _load_policy_file(self, path, force_reload):
        reloaded, data = _cache_handler.read_cached_file(
            self._file_cache, path, force_reload=force_reload)
        if reloaded or not self.rules:
            self.rules = jsonutils.loads(data)

    def _get_policy_path(self):
        """Locate the policy JSON data file/path.
        """
        policy_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(policy_dir, self.policy_file)

    def enforce(self, action, auth_info):
        """Checks permission against action

        :action api aciton to check permission
        :auth_info admin's auth_info, in following format:
            {
                'role': '',
                'privilege': 2
            }
        """
        if auth_info is None:
            raise apiExc.ActionPermissionDenied(message=u'Permission denied: user is inactive')

        self.load_rules()
        roles_needed = self.rules.get(action)

        # only check for permission if action in policy file
        if not roles_needed:
            return

        LOG.debug("auth_role: %s, role needed: %s" %(auth_info['role'], roles_needed))

        match_role = [r for r in auth_info['role'] if r in roles_needed]
        if not match_role:
            raise apiExc.ActionPermissionDenied(message=u'you do not have permission for this action: < %s >' % action)
