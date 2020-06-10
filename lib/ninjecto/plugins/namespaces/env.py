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
Namespace plugin to access environment variables.
"""

from re import match
from os import environ
from logging import getLogger
from collections import namedtuple


log = getLogger(__name__)


SLUG_REGEX = r'^[a-zA-Z][a-zA-Z0-9_]*$'


def namespace_env(config, filepath):
    """
    Fetch data from the environment.

    :param dict config: Plugin configuration, if any.
    :param Path filepath: Path file been rendered.

    :return: A named tuple with information from the environment.
    :rtype: namedtuple
    """

    env_safe = {
        key for key in environ.keys()
        if match(SLUG_REGEX, key)
    }
    env_available = set(environ.keys())
    env_ignored = env_available - env_safe

    if env_ignored:
        log.debug('Environment variables unsafe to load: {}'.format(
            sorted(env_ignored)
        ))

    env_type = namedtuple(
        'env',
        env_safe,
    )
    env = env_type(**{key: environ[key] for key in env_safe})

    log.debug('env namespace: {}'.format(env._replace(
        **{key: '****' for key in env_safe}
    )))
    return env


__all__ = [
    'namespace_env',
]
