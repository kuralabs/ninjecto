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
Core module.
"""

from logging import getLogger

from .local import load_local
from .plugins.filters import FiltersLoader
from .plugins.namespaces import NamespacesLoader


log = getLogger(__name__)


class Ninjecto:
    def __init__(self, values, source, destination):
        self._values = values
        self._source = source
        self._destination = destination

        self._local = load_local(self._source.parent)
        self._filters = FiltersLoader()
        self._namespaces = NamespacesLoader()

    def run(self, dry_run, override):
        self._filters.load_functions()
        self._namespaces.load_functions()
        log.info('{} -> {}'.format(self._source, self._destination))
        log.info('with:\n{}'.format(self._values))


__all__ = [
    'Ninjecto',
]
