# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2023 KuraLabs S.R.L
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
Values loading and merging module.
"""

from sys import stdin
from logging import getLogger

from pprintpp import pformat

from .utils.dictionary import update
from .inputs import load_files, load_content


log = getLogger(__name__)


def expand_dotdict(dotdict):
    """
    Expand a dictionary containing keys in dot notation.

    For example::

    .. code-block:: python3

        dotdict = {
            'key1.key2.key3': 'string1',
            'key1.key2.key4': 1000,
            'key4.key5': 'string2',
        }

        expanded = expand_dotdict(dotdict)

    Will produce:

    .. code-block:: python3

        {
            'key1': {
                'key2': {
                    'key3': 'string1',
                    'key4': 1000,
                },
            },
            'key4': {
                'key5': 'string2',
            },
        }

    :param dict dotdict: Original dictionary containing string keys in dot
     notation.

    :return: The expanded dictionary.
    :rtype: dict
    """
    dtype = type(dotdict)
    result = dtype()

    for key, value in dotdict.items():
        path = key.split('.')
        assert path, 'Invalid dot-notation path'

        node = result

        for part in path[:-1]:
            node = node.setdefault(part, dtype())
            assert isinstance(node, dtype), 'Incompatible paths to {}'.format(
                key,
            )

        node[path[-1]] = value

    return result


def load_values(values_files, values, values_in):
    """
    Get an unified data view of all values files, dot-notation values and
    standard input (if any).

    Merge is done left to right. That is, last to load will override last.

    :param list values_files: List of Path objects pointing to files with
     values for the rendering.
    :param OrderedDict values: Dictionary with keys in dot-notation and its
     associated values.
    :param str values_in: Read standard input using the given format. If None,
     then ignore standard input.

    :return: Normalized values loaded from all files and overrode with the
     values dictionary, if any.
    :rtype: dict
    """
    bundle = load_files(values_files)

    if values:
        log.debug(
            'Expanding dot-notation dictionary:\n{}'.format(pformat(values))
        )
        expanded = expand_dotdict(values)

        log.debug(
            'Expanded dot-notation dictionary:\n{}'.format(pformat(expanded))
        )
        update(bundle, expanded)

    if values_in:
        piped = load_content(stdin.read(), values_in)

        if piped:
            log.debug(
                'Parsed standard input:\n{}'.format(pformat(piped))
            )
            update(bundle, piped)

    if bundle:
        log.debug(
            'Final values bundle:\n{}'.format(pformat(bundle))
        )
    return bundle


__all__ = [
    'load_values',
]
