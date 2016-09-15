# -*- coding: utf-8 -*-

#
# Licensed Materials - Property of esse.io
#
# (C) Copyright esse.io. 2016 All Rights Reserved
#
# Author: Frank Han (frank@esse.io)
#
#

import base64
import bcrypt
from commutils.log import log as logging
LOG = logging.getLogger(__name__)


def gen_hashed_password(password):
    '''Hash a password with a randomly-generated salt
    '''
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def validate_hashed_password(password, hashed):
    '''Check that a unhashed password matches one that has previously been
      hashed
    :returns: True if passwd match, else False
    '''
    try:
        return (bcrypt.hashpw(password.encode('utf-8'),
                hashed.encode('utf-8')) == hashed)
    except Exception:
        return False


def obfuscate_str(stream):
    '''obfuscate string with base64 and rot13 encoding
    '''
    b64_str = base64.b64encode(stream)
    rot13_str = b64_str.encode('rot13')
    return rot13_str


def unobfuscate_str(obfuscated_str):
    '''unobfuscate string with base64 and rot13 encoding
    '''
    try:
        b64_str = obfuscated_str.decode('rot13')
        stream = base64.b64decode(b64_str)
    except Exception:
        LOG.error('failed to unobfuscate string: %s' % obfuscated_str)
        return None
    return stream


if __name__ == "__main__":
    obfuscated_str = obfuscate_str("hello,world")
    print 'obfuscated_str is: %s' % obfuscated_str
    unobfuscated_str = unobfuscate_str(obfuscated_str)
    print 'unobfuscated_str is: %s' % unobfuscated_str
