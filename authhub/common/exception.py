# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#


import authhub.common.error_code as ErrCode
from commutils.exception import ZenException


class InvalidSortKey(ZenException):
    msg_fmt = "Sort key supplied for db query was not valid."
    error_code = ErrCode.INTERNAL_SERVER_FAILURE


class InternalServerFailure(ZenException):
    msg_fmt = u"internal server failure: %(reason)s"
    error_code = ErrCode.INTERNAL_SERVER_FAILURE


class DBEntryAleadyExist(ZenException):
    '''
        the data already exist in database, like admin already exist
    '''
    msg_fmt = "data already exist in database: %(reason)s"
    error_code = ErrCode.DB_ENTRY_ALREADY_EXIST


class DBEntryNotExist(ZenException):
    '''
        the data does not exist in database
    '''

    msg_fmt = "data does not exist in database: %(reason)s"
    error_code = ErrCode.DB_ENTRY_NOT_EXIST


class InvalidRequestFormat(ZenException):
    '''
        the request format is not correct
    '''
    msg_fmt = u"invalid request format: %(reason)s"
    error_code = ErrCode.INVALID_REQUEST_FORMAT


class ActionPermissionDenied(ZenException):
    '''the request format is not correct
    '''
    msg_fmt = u"user are not allowed to take this action: %(reason)s"
    error_code = ErrCode.ACTION_PERMISSION_DENIED


class UserTokenExpired(ZenException):
    '''admin or family session expired
    '''
    msg_fmt = "user token has expired"
    error_code = ErrCode.USER_TOKEN_EXPIRED


class IncorrectUserOrPasswd(ZenException):
    '''invalid user or passwd when get token
    '''
    msg_fmt = "incorrect username or password"
    error_code = ErrCode.USER_OR_PASSWD_INCORRECT


class InvalidPasswdStrength(ZenException):
    '''passwd is so weak
    '''
    msg_fmt = u"password too weak"
    error_code = ErrCode.PASSWD_TOO_WEAK


class DBReferenceFailure(ZenException):
    '''db reference failure due to foreign key
    '''
    msg_fmt = u"db reference error met"
    error_code = ErrCode.DB_REFERENCE_FAILURE
