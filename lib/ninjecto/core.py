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

from pprintpp import pformat
from jinja2 import (
    Environment,
    select_autoescape,
    PrefixLoader, FileSystemLoader,
)


log = getLogger(__name__)


class Ninjecto:
    def __init__(
        self,
        config,
        local,
        filters,
        namespaces,
        libraries,
        values,
        source,
        destination,
    ):
        self._config = config

        self._local = local
        self._filters = filters
        self._namespaces = namespaces

        self._libraries = libraries

        self._values = values
        self._source = source
        self._destination = destination

    def run(self, dry_run, override):

        log.info('{} -> {}'.format(self._source, self._destination))
        log.info('With:\n{}'.format(self._values))

        log.info('Using filters:\n{}'.format(pformat(self._filters)))
        log.info('Using namespaces:\n{}'.format(pformat(self._namespaces)))

        config = self._config.ninjecto

        # Prepare environment
        envconf = dict(config.environment)
        envconf.update({
            'autoescape': select_autoescape(
                **config.autoescape,
            ),
            'loader': PrefixLoader({
                '': FileSystemLoader(
                    self._source.parent,
                    encoding=config.filesystemloader.encoding,
                    followlinks=config.filesystemloader.followlinks,
                ),
                'library': FileSystemLoader(
                    self._libraries,
                    encoding=config.filesystemloader.encoding,
                    followlinks=config.filesystemloader.followlinks,
                ),
            }),
        })
        environment = Environment(**envconf)

        for key, fltr in self._filters.items():
            environment.filters[key] = fltr

        # Render template
        template = environment.get_template(self._source.name)
        render = template.render(values={
            **self._namespaces,
            **{
                'values': self._values,
            }
        })

        # Write output
        if not dry_run:
            self._destination.parent.mkdir(parents=True, exist_ok=True)
            self._destination.write_text(
                render, encoding=config.output.encoding,
            )

        return render


__all__ = [
    'Ninjecto',
]
