# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2023 KuraLabs S.R.L
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
Supported input formats module.
"""

from logging import getLogger

from pprintpp import pformat

from .utils.dictionary import update


log = getLogger(__name__)


def load_json(content):
    """
    Load a string in JSON format.

    :param str content: String in JSON format.

    :return: A dictionary with the parsed content.
    :rtype: dict
    """
    from ujson import loads
    return loads(content)


def load_toml(content):
    """
    Load a string in TOML format.

    :param str content: String in TOML format.

    :return: A dictionary with the parsed content.
    :rtype: dict
    """
    from toml import loads
    return loads(content)


def load_yaml(content):
    """
    Load a string in YAML format.

    :param str content: String in YAML format.

    :return: A dictionary with the parsed content.
    :rtype: dict
    """
    from yaml import load, FullLoader
    return load(content, Loader=FullLoader)


SUPPORTED_FORMATS = {
    'toml': load_toml,
    'json': load_json,
    'yaml': load_yaml,
}


def load_content(content, frmt):
    """
    Load content in any supported file format.

    :param str content: String any supported file format.
    :param str frmt: The file format to parse the content for.

    :return: A dictionary with the parsed content.
    :rtype: dict
    """
    return SUPPORTED_FORMATS[frmt](content)


def load_file(path):
    """
    Load any supported file format.

    :param Path path: File to load.

    :return: A dictionary with the parsed content.
    :rtype: dict
    """
    frmt = path.suffix.replace('.', '', 1)
    if frmt not in SUPPORTED_FORMATS:
        raise RuntimeError(
            'Unknown file format "{}" for file {}. '
            'Supported formats are: {}.'.format(
                frmt, path,
                ', '.join(sorted(SUPPORTED_FORMATS.keys())),
            )
        )

    # Load file
    content = load_content(path.read_text(encoding='utf-8'), frmt)
    return content


def load_files(paths):
    """
    Recursively load a list of paths and merge their content left to right.

    That is, last to load will override last.

    :param list paths: List of Path objects pointing to files to load.

    :return: Merged content of all files.
    :rtype: dict
    """

    bundle = {}

    # Load files
    # The returned dict of a parsed file cannot be guaranteed consistently
    # ordered, so sadly here we loose sequentially of declaration in files.
    for file in paths:

        log.info(
            'Loading file {} ...'.format(file)
        )

        content = load_file(file)

        log.debug(
            'Content loaded:\n{}'.format(pformat(content))
        )

        # Update the general bundle
        update(bundle, content)

    if bundle:
        log.debug(
            'Final bundle:\n{}'.format(pformat(bundle))
        )

    return bundle


__all__ = [
    'SUPPORTED_FORMATS',
    'load_content',
    'load_file',
    'load_files',
]
