# -*- coding: utf-8 -*-

import sys
import six
import base64
import logging

LOG = logging.getLogger(__name__)


def safe_decode(text, encoding='utf-8', errors='strict'):
    """Decodes incoming text/bytes string using
    """
    if not isinstance(text, (six.string_types, six.binary_type)):
        raise TypeError("%s can't be decoded" % type(text))

    if isinstance(text, six.text_type):
        return text

    return text.decode(encoding, errors)


def safe_encode(text, encoding='utf-8'):
    """Encodes incoming text/bytes string using `encoding`.
    :raises TypeError: If text is not an instance of str
    """
    if not isinstance(text, (six.string_types, six.binary_type)):
        raise TypeError("%s can't be encoded" % type(text))

    try:
        return text.decode('utf-8')
    except Exception, e:
        try:
            return text.decode('gbk')
        except Exception, e:
            LOG.error('safe_encode error: [%s]' % (e))
            return ''


def exception_to_unicode(exc):
    """Get the message of an exception as a Unicode string.

    On Python 3, the exception message is always a Unicode string. On
    Python 2, the exception message is a bytes string *most* of the time.

    If the exception message is a bytes strings, try to decode it from UTF-8
    (superset of ASCII), from the locale encoding, or fallback to decoding it
    from ISO-8859-1 (which never fails).
    """
    msg = None
    if six.PY2:
        # First try by calling the unicode type constructor. We should try
        # unicode() before exc.__unicode__() because subclasses of unicode can
        # be easily casted to unicode, whereas they have no __unicode__()
        # method.
        try:
            msg = unicode(exc)
        except UnicodeError:
            # unicode(exc) fail with UnicodeDecodeError on Python 2 if
            # exc.__unicode__() or exc.__str__() returns a bytes string not
            # decodable from the default encoding (ASCII)
            if hasattr(exc, '__unicode__'):
                # Call directly the __unicode__() method to avoid
                # the implicit decoding from the default encoding
                try:
                    msg = exc.__unicode__()
                except UnicodeError:
                    pass

    if msg is None:
        # Don't call directly str(exc), because it fails with
        # UnicodeEncodeError on Python 2 if exc.__str__() returns a Unicode
        # string not encodable to the default encoding (ASCII)
        msg = exc.__str__()

    if isinstance(msg, six.text_type):
        # This should be the default path on Python 3 and an *optional* path
        # on Python 2 (if for some reason the exception message was already
        # in unicode instead of the more typical bytes string); so avoid
        # further converting to unicode in both of these cases.
        return msg

    try:
        # Try to decode from UTF-8 (superset of ASCII). The decoder fails
        # if the string is not a valid UTF-8 string: the UTF-8 codec includes
        # a validation algorithm to ensure the consistency of the codec.
        return msg.decode('utf-8')
    except UnicodeDecodeError:
        pass

    # Try the locale encoding, most error messages are encoded to this encoding
    # (ex: os.strerror(errno))
    encoding = sys.getfilesystemencoding()
    try:
        return msg.decode(encoding)
    except UnicodeDecodeError:
        pass

    # The encoding is not ASCII, not UTF-8, nor the locale encoding. Fallback
    # to the ISO-8859-1 encoding which never fails. It will produce mojibake
    # if the message is not encoded to ISO-8859-1, but we don't want a super
    # complex heuristic to get the encoding of an exception message.
    return msg.decode('latin1')


def base64_encode(src):
    ''' encode string to base64
    '''
    result = ''
    try:
        result = base64.standard_b64encode(src)
    except Exception as e:
        LOG.error('encode base64string error: [%s]' % e)
    return result


def base64_decode(src):
    ''' decode base64 encoded string
    '''
    result = ''
    try:
        result = base64.standard_b64decode(src)
    except Exception, e:
        LOG.error('decode base64string error: [%s]' % e)
    return result
