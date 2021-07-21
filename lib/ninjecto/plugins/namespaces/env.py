# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2021 KuraLabs S.R.L
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
Namespace plugin to access environment variables.
"""

from re import match
from os import environ
from logging import getLogger

from ...utils.dictionary import Namespace


log = getLogger(__name__)


SLUG_REGEX = r'^[a-zA-Z_][a-zA-Z0-9_]*$'


def namespace_env(config):
    """
    Fetch data from the environment.

    This function will filter the environment variables names that are
    considered "unsafe" to be represented as a Python variable. This is done to
    avoid crashing the code and the templates with weird environment variable
    names. This behavior can be disabled by setting
    ``ninjecto.namespace.env.safe`` to False.

    :param dict config: Plugin configuration, if any.

    :return: An object with information from the environment.
    :rtype: Namespace
    """

    env_available = set(environ.keys())

    if config.safe:

        env_safe = {
            key for key in env_available
            if match(SLUG_REGEX, key)
        }
        env_ignored = env_available - env_safe

        if env_ignored:
            log.info('Environment variables unsafe to load: {}'.format(
                ', '.join(sorted(env_ignored))
            ))

        env_available = env_safe

    env = Namespace({
        key: environ[key]
        for key in env_available
    })

    log.debug('env namespace: ({})'.format(
        ', '.join(sorted(env_available))
    ))
    return env


__all__ = [
    'namespace_env',
]
