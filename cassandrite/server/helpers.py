import datetime
import time


def unix_to_datetime(ts):
    try:
        return datetime.datetime.fromtimestamp(ts)
    except Exception:
        return None


def datetime_to_unix(dt):
    try:
        return time.mktime(dt.timetuple())
    except Exception:
        return None


def get_floor(ts, rule):
    # extract rule information
    interval = rule.split(':')[0]

    # convert ts to datetime
    dt = datetime.datetime.fromtimestamp(ts)

    # set floor
    if interval.endswith('s'):
        return datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    elif interval.endswith('m'):
        return datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0)
    elif interval.endswith('h'):
        return datetime.datetime(dt.year, dt.month, dt.day, dt.hour, 0, 0)
    elif interval.endswith('d'):
        return datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    else:
        return None


def get_ceiling(floor, rule):
    # extract rule information
    interval = rule.split(':')[0]
    offset = int(interval[:-1])

    # set ceiling
    if interval.endswith('s'):
        return floor + datetime.timedelta(seconds=offset)
    elif interval.endswith('m'):
        return floor + datetime.timedelta(minutes=offset)
    elif interval.endswith('h'):
        return floor + datetime.timedelta(hours=offset)
    elif interval.endswith('d'):
        return floor + datetime.timedelta(days=offset)
    else:
        return None


def get_ttl(ceiling, rule):
    # extract rule information
    interval = rule.split(':')[1]
    offset = int(interval[:-1])

    # copy ceiling
    c = datetime.datetime(ceiling.year, ceiling.month, ceiling.day, ceiling.hour, ceiling.minute, ceiling.second)

    # set ttl -- in seconds per cassandra docs
    if interval.endswith('s'):
        exp = c + datetime.timedelta(seconds=offset)
    elif interval.endswith('m'):
        exp = c + datetime.timedelta(minutes=offset)
    elif interval.endswith('h'):
        exp = c + datetime.timedelta(hours=offset)
    elif interval.endswith('d'):
        exp = c + datetime.timedelta(days=offset)
    elif interval.endswith('y'):
        exp = datetime.datetime(c.year + offset, c.month, c.day, c.hour, c.minute, c.second)
    else:
        return None

    # get current time
    now = datetime.datetime.now()

    # get diff
    diff = exp - now
    return int(diff.total_seconds())
