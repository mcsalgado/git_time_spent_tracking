#!/usr/bin/env python3

from datetime import timedelta
import re

TO_TIMEDELTA = {'weeks': timedelta(7),
                'week': timedelta(7),
                'w': timedelta(7),
                'days': timedelta(1),
                'day': timedelta(1),
                'd': timedelta(1),
                'hours': timedelta(0, 0, 0, 0, 0, 1),
                'hour': timedelta(0, 0, 0, 0, 0, 1),
                'h': timedelta(0, 0, 0, 0, 0, 1),
                'minutes': timedelta(0, 0, 0, 0, 1),
                'minute': timedelta(0, 0, 0, 0, 1),
                'min': timedelta(0, 0, 0, 0, 1),
                'm': timedelta(0, 0, 0, 0, 1),
                'seconds': timedelta(0, 1),
                'second': timedelta(0, 1),
                's': timedelta(0, 1)}


def day_hour_minute_second_string(td):
    # NOTE(mcsalgado): this is the same format as pandas.Timedelta
    days = td.days
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    ret = '{} days {:02}:{:02}:{:02}'.format(days, hours, minutes, seconds)
    return ret


# NOTE(mcsalgado): this is being used for the totals command
def hour_minute_second_string(td):
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    hours += td.days*24
    ret = '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)
    return ret


def parse_time(s):
    # NOTE(mcsalgado): break elements by commas, spaces and the 'and' word
    elements = re.split(r'(?:,)+|(?:\s+(?:and)?\s+)|\s+', s)

    tokens = []
    for element in elements:
        tokens.extend(_tokenize(element))

    ret = timedelta(0)
    for number, unit in zip(*(iter(tokens), )*2):
        ret += number * unit

    return ret


def _tokenize(s):
    first_pass = _tokenize_0(s)

    if first_pass:
        return first_pass

    elements_again = re.split(r'(\d+\.?\d*)|(\.\d+)', s)
    ret = []
    for e in elements_again:
        ret.extend(_tokenize_0(e))

    # NOTE(mcsalgado): hardcoded case for something like '1h30'
    if (len(ret) == 3 and isinstance(ret[0], int) and ret[1] == TO_TIMEDELTA['h'] and isinstance(ret[2], int)):
        ret.append(TO_TIMEDELTA['m'])
    return ret


def _tokenize_0(s):
    if s is None:
        return ()

    if s == '':
        return ()

    if s in TO_TIMEDELTA:
        return (TO_TIMEDELTA[s], )

    if s.isnumeric():
        return (int(s), )

    try:
        return (float(s), )
    except ValueError:
        pass

    if s == 'one':
        return (1, )

    hour_minute_second = re.match(r'(\d+):(\d+):(\d+)', s)
    if hour_minute_second:
        return (int(hour_minute_second.group(1)),
                TO_TIMEDELTA['hour'],
                int(hour_minute_second.group(2)),
                TO_TIMEDELTA['minute'],
                int(hour_minute_second.group(3)),
                TO_TIMEDELTA['second'])

    hour_minute = re.match(r'(\d+):(\d+)', s)
    if hour_minute:
        return (int(hour_minute.group(1)),
                TO_TIMEDELTA['hour'],
                int(hour_minute.group(2)),
                TO_TIMEDELTA['minute'])
    return ()


if __name__ == '__main__':
    assert '2 days 00:00:00' == day_hour_minute_second_string(parse_time('2 days'))
    assert '14 days 00:00:00' == day_hour_minute_second_string(parse_time('2 weeks'))
    assert '0 days 00:01:00' == day_hour_minute_second_string(parse_time('1 minute'))
    assert '0 days 00:21:00' == day_hour_minute_second_string(parse_time('21 min'))
    assert '0 days 03:00:00' == day_hour_minute_second_string(parse_time('3 hours'))
    assert '0 days 01:40:00' == day_hour_minute_second_string(parse_time('100 minutes'))
    assert '0 days 02:30:00' == day_hour_minute_second_string(parse_time('2 hours 30 minutes'))
    assert '0 days 02:30:00' == day_hour_minute_second_string(parse_time('2 hours and 30 minutes'))
    assert '0 days 00:32:00' == day_hour_minute_second_string(parse_time('2 minutes and 30 minutes'))
    assert '0 days 00:32:30' == day_hour_minute_second_string(parse_time('2 minutes and 30 minutes and 30 seconds'))
    assert '44 days 00:23:00' == day_hour_minute_second_string(parse_time('2 weeks 30 days 23 minutes'))
    assert '0 days 02:30:00' == day_hour_minute_second_string(parse_time('2:30'))
    assert '0 days 02:30:00' == day_hour_minute_second_string(parse_time('2:30:00'))

    # TODO(mcsalgado): these are weird... maybe I shouldn't allow it?
    assert '0 days 02:05:00' == day_hour_minute_second_string(parse_time('2:5'))
    assert '0 days 02:05:01' == day_hour_minute_second_string(parse_time('2:5:1'))

    assert '0 days 12:33:52' == day_hour_minute_second_string(parse_time('12:33:52'))
    assert '0 days 10:00:00' == day_hour_minute_second_string(parse_time('10h'))
    assert '1 days 00:00:00' == day_hour_minute_second_string(parse_time('24h'))
    assert '0 days 00:21:00' == day_hour_minute_second_string(parse_time('21min'))
    assert '0 days 02:30:00' == day_hour_minute_second_string(parse_time('2h30m'))
    assert '0 days 02:30:00' == day_hour_minute_second_string(parse_time('2h30'))
    assert '0 days 03:33:33' == day_hour_minute_second_string(parse_time('3h33m33s'))
    assert '1 days 01:30:00' == day_hour_minute_second_string(parse_time('1 day 1h30'))
    assert '1 days 01:30:00' == day_hour_minute_second_string(parse_time('1h30 1 day'))
    assert '0 days 03:00:00' == day_hour_minute_second_string(parse_time('1h30 1h30'))
    assert '0 days 00:00:02' == day_hour_minute_second_string(parse_time('2s'))
    assert '0 days 12:33:52' == day_hour_minute_second_string(parse_time('0 days 12:33:52'))
    assert '5 days 12:33:52' == day_hour_minute_second_string(parse_time('12:33:52 5 days'))
    assert '32 days 00:00:00' == day_hour_minute_second_string(parse_time('032 days'))
    assert '0 days 01:22:00' == day_hour_minute_second_string(parse_time('1 hour, 22 minutes'))
    assert '0 days 01:22:00' == day_hour_minute_second_string(parse_time('1 hour,22 minutes'))
    assert '0 days 01:22:00' == day_hour_minute_second_string(parse_time('1hour22minutes'))
    assert '0 days 01:22:00' == day_hour_minute_second_string(parse_time('1hour,22minutes'))
    assert '1 days 00:00:00' == day_hour_minute_second_string(parse_time('one day'))

    assert '0 days 00:30:00' == day_hour_minute_second_string(parse_time('0.5h'))
    assert '0 days 00:30:00' == day_hour_minute_second_string(parse_time('.5h'))
    assert '0 days 00:15:00' == day_hour_minute_second_string(parse_time('0.25h'))
    assert '0 days 01:00:00' == day_hour_minute_second_string(parse_time('1.h'))

    # TODO(mcsalgado): chinese is accepted but it means nothing huh
    # maybe it shouldn't be accepted at all
    assert '0 days 04:00:00' != day_hour_minute_second_string(parse_time('四h'))
    assert '0 days 00:00:00' == day_hour_minute_second_string(parse_time('四h'))

    assert '1056:23:00' == hour_minute_second_string(parse_time('2 weeks 30 days 23 minutes'))

    print('All tests passed.')
