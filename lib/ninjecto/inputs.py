# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2019 KuraLabs S.R.L
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


log = getLogger(__name__)


def load_json(path):
    """
    Load a file in JSON format.

    :param Path path: Path to the JSON file.

    :return: A dictionary with the parsed content.
    :rtype: dict
    """
    from ujson import loads
    return loads(path.read_text(encoding='utf-8'))


def load_toml(path):
    """
    Load a file in TOML format.

    :param Path path: Path to the TOML file.

    :return: A dictionary with the parsed content.
    :rtype: dict
    """
    from toml import loads
    return loads(path.read_text(encoding='utf-8'))


def load_yaml(path):
    """
    Load a file in YAML format.

    :param Path path: Path to the YAML file.

    :return: A dictionary with the parsed content.
    :rtype: dict
    """
    from yaml import load, FullLoader
    return load(path.read_text(encoding='utf-8'), Loader=FullLoader)


def load_file(path):
    """
    Load any supported file format.

    :param Path path: File to load.

    :return: A dictionary with the parsed content.
    :rtype: dict
    """
    extension = path.suffix
    if extension not in load_file.supported_formats:
        raise RuntimeError(
            'Unknown file format "{}" for file {}. '
            'Supported formats are :{}.'.format(
                extension, path,
                ', '.join(sorted(load_file.supported_formats.keys())),
            )
        )

    # Load file
    content = load_file.supported_formats[extension](path)
    return content


load_file.supported_formats = {
    '.toml': load_toml,
    '.json': load_json,
    '.yaml': load_yaml,
}


__all__ = [
    'load_file',
]
