# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 KuraLabs S.R.L
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Utilities to handle ISO 8601 formatted dates.
"""

from datetime import datetime
from functools import partial
from json import dumps, JSONEncoder


ISO8601_FORMAT = '%Y-%m-%dT%H:%M:%S'


def iso8601_to_datetime(date_string):
    """
    Converts a date of the format YYYY:MM:DDTHH:MM:SS (ISO 8601) to
    a datetime object.

    This function is somewhat analogous to::

        from datetime import datetime
        datetime.fromisoformat('2019-08-05T14:38:13')

    But since :py:func:`datetime.fromisoformat` was added only in
    Python 3.7 this function is left for backward compatibility.

    :param str date_string: Date string.
    :return: Datetime object.
    """
    return datetime.strptime(date_string, ISO8601_FORMAT)


def datetime_to_iso8601(date):
    """
    Converts a datetime object to a date string of the format
    YYYY:MM:DDTHH:MM:SS (ISO 8601).

    This function is analogous to::

        from datetime import datetime
        datetime.now().replace(microsecond=0).isoformat()

    :param datetime date: Datetime object.
    :return: string with the date.
    """
    return datetime.strftime(date, ISO8601_FORMAT)


class DateTimeJSONEncoder(JSONEncoder):
    """
    Custom JSON enconder that converts any datetime object to a ISO 8601
    date string.
    """

    def default(self, o):
        if isinstance(o, datetime):
            return datetime_to_iso8601(o)
        return JSONEncoder.default(self, o)


json_dumps = partial(dumps, cls=DateTimeJSONEncoder)
"""
A json.dumps compatible function that knows how to serialize datetime objects
into ISO 8601 strings.
"""


__all__ = [
    'iso8601_to_datetime',
    'datetime_to_iso8601',
    'DateTimeJSONEncoder',
    'json_dumps',
]
