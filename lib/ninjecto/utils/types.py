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
Utilities to convert string to other data types.
"""

from .iso8601 import iso8601_to_datetime


def booleanize(value):
    """
    Convert a string to a boolean.

    :raises: ValueError if unable to convert.

    :param str value: String to convert.

    :return: True if value in lowercase matches "true" or "yes"; False if value
     in lowercase matches "false"or "no".
    :rtype: bool
    """
    valuemap = {
        'true': True,
        'yes': True,
        'false': False,
        'no': False,
    }
    casted = valuemap.get(value.lower(), None)
    if casted is None:
        raise ValueError(str(value))
    return casted


def autocast(value):
    """
    Try to convert a string to some basic data types.

    :param str value: The string to try to convert.

    :return: This function will try to convert a string to a:

     - ``datetime``, if string is in ISO8601 with timezone format.
     - ``int``, if succeeds.
     - ``float``, if succeeds.
     - ``boolean``, using the :py:func:`booleanize` function.

     If all the above fails, the source string is returned as-is.

    :rtype: Any of the above.
    """
    for caster in [
        iso8601_to_datetime,
        int,
        float,
        booleanize,
    ]:
        try:
            return caster(value)
        except Exception:
            continue
    return value


__all__ = [
    'booleanize',
    'autocast',
]
