"""
UUID related utilities and helper functions.
"""

import uuid


def generate_uuid():
    """Creates a random uuid string.

    :returns: string
    """
    return str(uuid.uuid4())


def _format_uuid_string(string):
    return (string.replace('urn:', '')
                  .replace('uuid:', '')
                  .strip('{}')
                  .replace('-', '')
                  .lower())


def is_uuid_like(val):
    """Returns validation of a value as a UUID.

    :param val: Value to verify
    :type val: string
    :returns: bool
    """
    try:
        return str(uuid.UUID(val)).replace('-', '') == _format_uuid_string(val)
    except (TypeError, ValueError, AttributeError):
        return False
