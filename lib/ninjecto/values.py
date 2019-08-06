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
from collections import Mapping

from pprintpp import pformat

from .inputs import load_file


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


def update(to_update, update_with):
    """
    Recursively update a dictionary with another.

    :param dict to_update: Dictionary to update.
    :param dict update_with: Dictionary to update with.

    :return: The first dictionary recursively updated by the second.
    :rtype: dict
    """
    for key, value in update_with.items():

        if not isinstance(value, Mapping):
            to_update[key] = value
            continue

        to_update[key] = update(
            to_update.get(key, type(value)()),
            value,
        )

    return to_update


def load_values(values_files, values):
    """
    :param list values_files: List of Path objects pointing to files with
     values for the rendering.
    :param OrderedDict values: Dictionary with keys in dot-notation and its
     associated values.

    :return: Normalized values loaded from all files and overrode with the
     values dictionary, if any.
    :rtype: dict
    """

    bundle = {}

    # Load files
    # The returned dict of a parsed file cannot be guaranteed consistently
    # ordered, so sadly here we loose sequentially of declaration in files.
    if values_files:
        for values_file in values_files:

            log.info(
                'Loading values file {} ...'.format(values_file)
            )

            content = load_file(values_file)

            log.debug(
                'Values loaded:\n{}'.format(pformat(content))
            )

            # Update the general bundle
            update(bundle, content)

    if values:
        log.debug(
            'Expanding dot-notation dictionary:\n{}'.format(pformat(values))
        )
        expanded = expand_dotdict(values)

        log.debug(
            'Expanded dot-notation dictionary:\n{}'.format(pformat(expanded))
        )
        update(bundle, expanded)

    log.debug(
        'Final values bundle:\n{}'.format(pformat(bundle))
    )
    return bundle


__all__ = [
    'load_values',
]
