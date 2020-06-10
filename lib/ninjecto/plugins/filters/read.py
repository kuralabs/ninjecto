# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 KuraLabs S.R.L
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
Filter to read the content of text files.
"""

from pathlib import Path


def filter_read(filename, encoding='utf-8', errors='strict'):
    """
    Filter to read the content of text files.

    :param filename: Path object or string to the file to read from.
    :param str encoding: The name of the encoding used to decode the content of
     the file.
    :param str errors: Specifies how encoding and decoding errors are to be
     handled. Refer to Python's open() function documentation.

    :return: The totality of the content of the file.
    :rtype: str
    """
    return Path(filename).read_text(encoding='utf-8', errors=errors)


__all__ = [
    'filter_read',
]
