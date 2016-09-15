# -*- coding: utf-8 -*-
#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

import string
from authhub.common import exception as EXC


class passwd_strength_checker(object):
    '''this class is used to check passwd strength
    '''
    def __init__(self):
        pass

    def _check_length(self, passwd):
        """
        check whehter passwd length is enough
        """
        if len(passwd) < 6:
            return False
        elif len(passwd) >= 6 and len(passwd) <= 20:
            return True
        else:
            return False

    def _check_digital(self, passwd):
        """
        check wheter passwd contains digital
        """
        for char in passwd:
            if char.isdigit():
                return True
        return False

    def _check_lower(self, passwd):
        """
        check whether passwd contains lower character
        """
        for char in passwd:
            if char.islower():
                return True
        return False

    def _check_upper(self, passwd):
        """
        check whether passwd contains upper character
        """
        for char in passwd:
            if char.isupper():
                return True
        return False

    def _check_punctuation(self, passwd):
        """
        check whether passwd contains uppper character
        """
        invalidchar = set(string.punctuation)
        for char in passwd:
            if char in invalidchar:
                return True
        return False

    def check_passwd_strength(self, passwd):
        """
        check passwd strength
        """
        if not self._check_length(passwd):
            raise EXC.InvalidPasswdStrength()
        return
        # currently we only check strength
        has_digital = self._check_digital(passwd)
        has_lower = self._check_lower(passwd)
        has_upper = self._check_upper(passwd)
        has_ptt = self._check_punctuation(passwd)
        # asswd must contains at least two kinds of character
        if not ((has_digital or has_lower or has_upper) and
                (has_digital or has_lower or has_ptt) and
                (has_digital or has_upper or has_ptt) and
                (has_lower or has_upper or has_ptt)):

            raise EXC.InvalidPasswdStrength()
