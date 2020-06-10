# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 KuraLabs S.R.L
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

from functools import partial
from datetime import datetime
from json import JSONEncoder, dumps as jsondumps


ISO8601_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'


def iso8601_to_datetime(whenstr):
    """
    Converts a date in the ISO8601 with timezone format to a datetime object
    with timezone.

    The format is of the form `` YYYY-MM-DDTHH:MM:SS.MS-TZ``, for example::

        2020-06-10T01:47:35.186550-06:00

    Prior to Python 3.7, :py:meth:`datetime.datetime.strptime()` *``%z``* was
    only able to parse the timezone when using the ``±HHMM[SS[.ffffff]]``
    format.

    To workaround this limitation, we literally strip the last
    (first rightmost) colon using::

        ''.join(now.rsplit(':', 1))

    And that's enough to make :py:meth:`datetime.datetime.strptime()` to parse
    ISO8601 with timezone dates correctly and is compatible with any Python
    version 3.5 or higher.

    :param str whenstr: ISO8601 with timezone datetime string.

    :return: Datetime object with timezone.
    :rtype: :py:class:`datetime.datetime`
    """
    return datetime.strptime(''.join(whenstr.rsplit(':', 1)), ISO8601_FORMAT)


def datetime_to_iso8601(whendt):
    """
    Converts a datetime object to a date string of the ISO8601 with timezone.

    The format is of the form ``YYYY-MM-DDTHH:MM:SS.MS-TZ``, for example::

        2020-06-10T01:47:35.186550-06:00

    :param datetime whendt: Datetime object. *Any naive datetime object is
     considered a local timezone datetime.* To correctly pass a UTC datetime
     use::

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)

    :return: A string with the datetime in the ISO8601 with timezone format.
    :rtype: str
    """
    # Any naive datetime is a local timezone datetime
    if whendt.tzinfo is None:
        whendt = whendt.astimezone(tz=None)
    return whendt.isoformat()


class DateTimeJSONEncoder(JSONEncoder):
    """
    Custom JSON enconder that converts any datetime object to a ISO 8601
    date string.
    """

    def default(self, o):
        if isinstance(o, datetime):
            return datetime_to_iso8601(o)
        return JSONEncoder.default(self, o)


dumps = partial(jsondumps, cls=DateTimeJSONEncoder)
"""
A json.dumps compatible function that knows how to serialize datetime objects
into ISO 8601 strings.
"""


__all__ = [
    'iso8601_to_datetime',
    'datetime_to_iso8601',
    'DateTimeJSONEncoder',
    'dumps',
]
__api__ = [
    'iso8601_to_datetime',
    'datetime_to_iso8601',
    'DateTimeJSONEncoder',
]
