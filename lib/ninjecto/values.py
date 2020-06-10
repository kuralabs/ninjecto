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
Values loading and merging module.
"""

from logging import getLogger

from pprintpp import pformat

from .inputs import load_files
from .utils.dictionary import update


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


def load_values(values_files, values):
    """
    Get an unified data view of all values files and dot-notation values.

    Merge is done right to left.

    :param list values_files: List of Path objects pointing to files with
     values for the rendering.
    :param OrderedDict values: Dictionary with keys in dot-notation and its
     associated values.

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

    if bundle:
        log.debug(
            'Final values bundle:\n{}'.format(pformat(bundle))
        )
    return bundle


__all__ = [
    'load_values',
]
