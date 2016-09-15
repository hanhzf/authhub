"""
Time related utilities and helper functions.
"""

import calendar
import datetime
import time

import iso8601
from pytz import timezone, utc
import six

# ISO 8601 extended time format with microseconds
# _ISO8601_TIME_FORMAT_SUBSECOND = '%Y-%m-%dT%H:%M:%S.%f'

# _ISO8601_TIME_FORMAT_SUBSECOND = '%Y-%m-%dT%H:%M:%S'
# _ISO8601_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

_ISO8601_TIME_FORMAT_SUBSECOND = '%Y-%m-%d %H:%M:%S'
_ISO8601_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
PERFECT_TIME_FORMAT = _ISO8601_TIME_FORMAT_SUBSECOND
PERFECT_DATE_FORMAT = '%Y-%m-%d'
PERFECT_HOUR_MINIUTE_FORMAT = '%H:%M'

_MAX_DATETIME_SEC = 59


try:
    now = time.monotonic
except AttributeError:
    try:
        # Try to use the pypi module if it's available (optionally...)
        from monotonic import monotonic as now
    except (AttributeError, ImportError):
        # Ok fallback to the non-monotonic one...
        now = time.time


def isotime(at=None, subsecond=False):
    """Stringify time in ISO 8601 format.

    .. deprecated:: > 1.5.0
       Use :func:`utcnow` and :func:`datetime.datetime.isoformat` instead.
    """
    if not at:
        at = utcnow()
    st = at.strftime(_ISO8601_TIME_FORMAT
                     if not subsecond
                     else _ISO8601_TIME_FORMAT_SUBSECOND)
    tz = at.tzinfo.tzname(None) if at.tzinfo else 'UTC'
    st += ('Z' if tz == 'UTC' else tz)
    return st


def parse_isotime(timestr):
    """Parse time from ISO 8601 format."""
    try:
        return iso8601.parse_date(timestr)
    except iso8601.ParseError as e:
        raise ValueError(six.text_type(e))
    except TypeError as e:
        raise ValueError(six.text_type(e))


def strtime(at=None, fmt=PERFECT_TIME_FORMAT):
    """Returns formatted utcnow.

    .. deprecated:: > 1.5.0
       Use :func:`utcnow()`, :func:`datetime.datetime.isoformat`
       or :func:`datetime.strftime` instead.

       strtime() => utcnow().isoformat()
       strtime(fmt=...) => utcnow().strftime(fmt)
       strtime(at) => at.isoformat()
       strtime(at, fmt) => at.strftime(fmt)
    """
    if not at:
        at = utcnow()
    return at.strftime(fmt)


def strdate(at=None, fmt=PERFECT_DATE_FORMAT):
    """Returns formatted date.
    """
    if not at:
        at = utcnow()
    return at.strftime(fmt)


def parse_strtime(timestr, fmt=PERFECT_TIME_FORMAT):
    """Turn a formatted time back into a datetime."""
    return datetime.datetime.strptime(timestr, fmt)


def parse_strdate(datestr, fmt=PERFECT_DATE_FORMAT):
    """Turn a formatted date back into a date."""
    dt = datetime.datetime.strptime(datestr, fmt)
    return datetime.date(dt.year, dt.month, dt.day)


def normalize_time(timestamp):
    """Normalize time in arbitrary timezone to UTC naive object."""
    offset = timestamp.utcoffset()
    if offset is None:
        return timestamp
    return timestamp.replace(tzinfo=None) - offset


def is_older_than(before, seconds):
    """Return True if before is older than seconds.
    """
    # add china timezone info to before
    if before.find('+08:00') == -1:
        before = before + '+08:00'

    if isinstance(before, six.string_types):
        before = parse_isotime(before)

    before = normalize_time(before)
    nowtime = normalize_time(utcnow())

    return nowtime - before > datetime.timedelta(seconds=seconds)


def is_newer_than(after, seconds):
    """Return True if after is newer than seconds."""
    # add china timezone info to before
    if after.find('+08:00') == -1:
        after = after + '+08:00'

    if isinstance(after, six.string_types):
        after = parse_isotime(after)

    after = normalize_time(after)
    nowtime = normalize_time(utcnow())

    return after - nowtime > datetime.timedelta(seconds=seconds)


def utcnow_delta_ts(microsecond=False, deltaseconds=0):
    """Timestamp version of our utcnow function.

    See :py:class:`common.utils.fixture.TimeFixture`.

    """
    now = utcnow()
    timestamp = calendar.timegm(now.timetuple())
    if microsecond:
        timestamp += float(now.microsecond) / 1000000

    return timestamp + deltaseconds


def utcnow(with_timezone=False):
    """Overridable version of utils.utcnow that can return a TZ-aware datetime.

    See :py:class:`common.utils.fixture.TimeFixture`.

    """
    if utcnow.override_time:
        try:
            return utcnow.override_time.pop(0)
        except AttributeError:
            return utcnow.override_time
    if with_timezone:
        return datetime.datetime.now(tz=iso8601.iso8601.UTC)
        # return datetime.datetime.now(tz=timezone('Asia/Harbin'))
    return datetime.datetime.utcnow()


utcnow.override_time = None


def set_time_override(override_time=None):
    """Overrides utils.utcnow.

    Make it return a constant time or a list thereof, one at a time.

    See :py:class:`common.utils.fixture.TimeFixture`.

    :param override_time: datetime instance or list thereof. If not
                          given, defaults to the current UTC time.
    """
    utcnow.override_time = override_time or datetime.datetime.utcnow()


def advance_time_delta(timedelta):
    """Advance overridden time using a datetime.timedelta.

    See :py:class:`common.utils.fixture.TimeFixture`.

    """
    assert utcnow.override_time is not None
    try:
        for dt in utcnow.override_time:
            dt += timedelta
    except TypeError:
        utcnow.override_time += timedelta


def advance_time_seconds(seconds):
    """Advance overridden time by seconds.

    See :py:class:`common.utils.fixture.TimeFixture`.

    """
    advance_time_delta(datetime.timedelta(0, seconds))


def get_advance_time_days(num_days):
    """  return datetime of num_days days later
    """
    current_date = utcnow()
    result = current_date + datetime.timedelta(days=num_days)
    return result


def get_advance_time(num_days=0, num_hours=0, num_seconds=0):
    """  return datetime of num_days, num_hours, num_seconds later
    """
    current_date = utcnow()
    result = current_date + datetime.timedelta(days=num_days,
                                               hours=num_hours,
                                               seconds=num_seconds)
    return result


def clear_time_override():
    """Remove the overridden time.

    See :py:class:`common.utils.fixture.TimeFixture`.

    """
    utcnow.override_time = None


def marshall_now(now=None):
    """Make an rpc-safe datetime with microseconds."""
    if not now:
        now = utcnow()
    d = dict(day=now.day, month=now.month, year=now.year, hour=now.hour,
             minute=now.minute, second=now.second,
             microsecond=now.microsecond)
    if now.tzinfo:
        d['tzname'] = now.tzinfo.tzname(None)
    return d


def unmarshall_time(tyme):
    """Unmarshall a datetime dict."""

    # NOTE(ihrachys): datetime does not support leap seconds,
    # so the best thing we can do for now is dropping them
    # http://bugs.python.org/issue23574
    second = min(tyme['second'], _MAX_DATETIME_SEC)
    dt = datetime.datetime(day=tyme['day'],
                           month=tyme['month'],
                           year=tyme['year'],
                           hour=tyme['hour'],
                           minute=tyme['minute'],
                           second=second,
                           microsecond=tyme['microsecond'])
    tzname = tyme.get('tzname')
    if tzname:
        tzinfo = timezone(tzname)
        dt = tzinfo.localize(dt)
    return dt


def delta_seconds(before, after):
    """Return the difference between two timing objects.

    Compute the difference in seconds between two date, time, or
    datetime objects (as a float, to microsecond resolution).
    """
    delta = after - before
    return total_seconds(delta)


def total_seconds(delta):
    """Return the total seconds of datetime.timedelta object.

    Compute total seconds of datetime.timedelta, datetime.timedelta
    doesn't have method total_seconds in Python2.6, calculate it manually.
    """
    try:
        return delta.total_seconds()
    except AttributeError:
        return ((delta.days * 24 * 3600) + delta.seconds +
                float(delta.microseconds) / (10 ** 6))


def is_soon(dt, window):
    """Determines if time is going to happen in the next window seconds.

    :param dt: the time
    :param window: minimum seconds to remain to consider the time not soon

    :return: True if expiration is within the given duration
    """
    soon = (utcnow() + datetime.timedelta(seconds=window))
    return normalize_time(dt) <= soon


def local_to_utc(local_dt):
    '''change localtime to UTC
    :param datetime local_dt: default local time
    :return: utc datetime
    :rtype: datetime
    '''
    if local_dt is None:
        return None
    tz = 'Asia/Harbin'
    local_tz = timezone(tz)
    local_dt = local_tz.localize(local_dt, is_dst=None)
    utc_dt = local_dt.astimezone(utc)
    return utc_dt


def utc_to_local(utc_dt):
    '''change UTC time to localtime
    :param datetime utc_dt: utc time
    :return: local datetime
    :rtype: datetime
    '''
    if utc_dt is None:
        return None
    local_tz = timezone('Asia/Harbin')
    local_dt = utc_dt.replace(tzinfo=utc).astimezone(local_tz)
    return local_dt


def strtime_utc_to_local(utc_dt, fmt=None):
    '''change UTC time to localtime
    :param datetime utc_dt: utc datetime
    :return: local datetime
    :rtype: str
    '''
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M:%S'
    return strtime(utc_to_local(utc_dt), fmt)


def strtime_local_to_utc(local_dt, fmt=None):
    '''change local time to utc time
    :param datetime local_dt: local datetime
    :return: utc datetime
    :rtype: str
    '''
    if fmt is None:
        fmt = '%Y-%m-%d %H:%M:%S'
    return strtime(local_to_utc(local_dt), fmt)


def get_local_now():
    '''get localtime
    :return: localnow datetime
    :rtype: datetime
    '''
    utc_dt = utcnow()
    return utc_to_local(utc_dt)


if __name__ == '__main__':
    test_date = '2016-04-23 07:02:23'
    print local_to_utc(test_date)
    print utc_to_local(test_date)
    print get_local_now()
