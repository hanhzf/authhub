# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

# error codes
INTERNAL_SERVER_FAILURE = 1000
INVALID_REQUEST_FORMAT = 1002
DB_ENTRY_ALREADY_EXIST = 1003   # db record already exist
DB_ENTRY_NOT_EXIST = 1004       # db record does not exist
DB_REFERENCE_FAILURE = 1005       # due to foreign key

USER_TOKEN_EXPIRED = 1006
USER_OR_PASSWD_INCORRECT = 1007
ACTION_PERMISSION_DENIED = 1008
PASSWD_TOO_WEAK = 1009
