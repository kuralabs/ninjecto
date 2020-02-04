# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020 KuraLabs S.R.L
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
Configuration loading module.
"""

from os import environ
from pathlib import Path
from logging import getLogger

from pkg_resources import resource_filename

from .inputs import load_file, load_files
from .utils.git import find_root, GitError


log = getLogger(__name__)


def load_config(configs):
    """
    Load Ninjecto's default, system's, user's, project's and given
    configuration.

    The algorithm loads files in the following order:

    #. Package's default configuration.
    #. System's configuration from ``/etc/ninjecto/config.xxx``
    #. User's configuration from
       ``$XDG_CONFIG_HOME/ninjecto/config.xxx`` or
       ``$HOME/.config/ninjecto/config.xxx`` if
       ``$XDG_CONFIG_HOME`` is unavailable.
    #. User's "alternative" configuration from ``$HOME/.ninjerc.xxx``.
    #. Project's global configuration from ``<gitroot>/.ninjerc.xxx``
       ``<gitroot>`` is determined by :func:`ninjecto.utils.git.find_root`.
       Currently, ``git`` is the only version control system supported.
    #. Project's "high-priority" local configuration from
       ``$PWD/.ninjerc.xxx``, but only if $PWD is different from the <gitroot>
       (if available).
    #. Additional given configuration files, in order.

    :param list configs: List of paths to configurations files to load.

    :return: Final and merged configuration.
    :rtype: dict
    """

    try:
        gitroot = Path(find_root())
    except GitError:
        gitroot = None

    files = [
        Path(
            resource_filename(__package__, 'data/config.yaml')
        ),
        *(
            Path('/etc/ninjecto/config{}'.format(frmt))
            for frmt in load_file.supported_formats
        ),
        *(
            Path(environ.get(
                'XDG_CONFIG_HOME',
                Path.home() / '.config',
            )) / 'ninjecto' / 'config{}'.format(frmt)
            for frmt in load_file.supported_formats
        ),
        *(
            Path.home() / '.ninjerc{}'.format(frmt)
            for frmt in load_file.supported_formats
        ),
        *(
            tuple() if gitroot is None
            else (
                gitroot / '.ninjerc{}'.format(frmt)
                for frmt in load_file.supported_formats
            )
        ),
        *(
            tuple() if gitroot is not None and gitroot == Path.cwd()
            else (
                Path.cwd() / '.ninjerc{}'.format(frmt)
                for frmt in load_file.supported_formats
            )
        ),
        *configs,
    ]

    log.debug('Configuration files:')
    valid = []

    for file in files:
        if not file.exists():
            log.debug('{} doesn\'t exists ...'.format(file))
            continue

        if file.is_file():
            log.debug('{} exists as is going to be loaded ...'.format(file))
            valid.append(file)
            continue

        log.warning(
            'Configuration file {} exists but is not a regular file. '
            'Ignoring ...'.format(file)
        )

    # FIXME: Maybe avoid breaking a system if the non-explicitly given
    #        configuration files are broken?
    log.debug('Loading configuration:')
    return load_files(valid)


__all__ = [
    'load_config',
]
