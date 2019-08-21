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
Module implementing the load of local ninjeconf.py files.
"""

import sys
from pathlib import Path
from logging import getLogger
from importlib import import_module


log = getLogger(__name__)


PREVIOUS = None


def load_local(rootpath):
    """
    Try to load local configurations from ninjeconf.py file from the given root
    directory.

    :param Path rootpath: Path to the root directory to load local
     configuration from.

    :return: The ninjeconf module loaded.
    :rtype: module
    """

    # Check the module exists
    ninjeconf = rootpath / 'ninjeconf.py'

    if not ninjeconf.is_file():
        log.debug('No local ninjeconf.py found.')
        return

    import_path = str(rootpath.resolve())

    # Remove previous module if exists
    global PREVIOUS
    if PREVIOUS is not None:
        del sys.modules['ninjeconf']
        sys.path.remove(PREVIOUS)

    # Import module
    sys.path.append(import_path)
    module = import_module('ninjeconf')
    PREVIOUS = import_path

    # Check the right module was loaded
    if Path(module.__file__) != ninjeconf:
        raise RuntimeError('Wrong ninjeconf.py module loaded! {} != {}'.format(
            Path(module.__file__).resolve(),
            ninjeconf.resolve(),
        ))

    log.info(
        'Local ninjeconf.py successfully loaded from {}'.format(import_path)
    )

    return module


__all__ = [
    'load_local'
]
