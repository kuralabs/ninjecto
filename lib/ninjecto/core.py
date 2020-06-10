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
Core module.
"""

from logging import getLogger

from pprintpp import pformat
from jinja2 import (
    select_autoescape,
    Environment,
    ChoiceLoader,
    DictLoader,
    PrefixLoader,
    FileSystemLoader,
)
from jinja2 import (
    Undefined,
    ChainableUndefined,
    DebugUndefined,
    StrictUndefined,
)

from .utils.dictionary import Namespace


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
        filename,
    ):
        self._config = Namespace(config)

        self._local = local
        self._filters = filters
        self._namespaces = namespaces

        self._libraries = libraries

        self._values = values
        self._source = source
        self._destination = destination
        self._filename = filename

        self.undefmap = {
            'Undefined': Undefined,
            'ChainableUndefined': ChainableUndefined,
            'DebugUndefined': DebugUndefined,
            'StrictUndefined': StrictUndefined,
        }

    def run(self, dry_run=False, override=False, levels=None):

        log.info('{} -> {}'.format(self._source, self._destination))
        log.info('With:\n{}'.format(self._values))

        log.info('Using filters:\n{}'.format(pformat(self._filters)))
        log.info('Using namespaces:\n{}'.format(pformat(self._namespaces)))

        self._dry_run = dry_run
        self._override = override
        self._levels = levels
        return self.process_file(
            self._source,
            self._destination,
            self._filename,
            self._levels,
        )

    def process_file(self, src, dstdir, filename=None, levels=None):
        config = self._config.ninjecto
        dry_run = self._dry_run
        override = self._override

        if levels is not None and levels < 1:
            return 0

        # First thing first, render the filename
        if filename is None:
            filename = self.render(src.name, src.name)

            # The file rendered as empty, which usually implies a conditional
            # file, so we stop the process
            if not filename.strip():
                log.warning(
                    '"{}" file renders to nothing, skipping ...'.format(
                        src.name
                    )
                )
                return 0

        # Now with the name, we have an output
        dst = dstdir / filename

        # Check override
        if dst.exists() and not override:
            raise RuntimeError(
                '{} exists. '
                'Use --force to override files and directories.'.format(
                    dst,
                )
            )

        # Check if file, if file, render content and write
        if src.is_file():
            content = self.render(
                src.name,
                src.read_text(encoding=config.input.encoding)
            )
            if not dry_run:
                dst.write_text(
                    content, encoding=config.output.encoding,
                )
                dst.chmod(src.stat().st_mode)

            return 1

        # If directory, recurse into it
        elif src.is_dir():

            if not dry_run:
                dst.mkdir(exist_ok=override)
                dst.chmod(src.stat().st_mode)

            processed = 1
            levels = None if levels is None else levels - 1

            for subfile in src.iterdir():
                processed += self.process_file(
                    subfile, dst,
                    filename=None,
                    levels=levels,
                )

            return processed

        raise RuntimeError(
            '{} isn\'t a file nor directory. '
            'Don\'t know what to do.'.format(src)
        )

    def render(self, name, content):
        # Optimization for empty files
        if not content:
            return ''

        config = self._config.ninjecto

        # Prepare environment
        envconf = dict(config.environment)
        envconf.update({
            'undefined': self.undefmap[config.undefined.clss],
            'autoescape': select_autoescape(
                **dict(config.autoescape),
            ),
            'loader': ChoiceLoader([
                DictLoader({
                    name: content,
                }),
                PrefixLoader({
                    'library': FileSystemLoader(
                        self._libraries,
                        encoding=config.filesystemloader.encoding,
                        followlinks=config.filesystemloader.followlinks,
                    ),
                }),
            ]),
        })
        environment = Environment(**envconf)

        # Make filters available
        for key, fltr in self._filters.items():
            environment.filters[key] = fltr

        # Make namespaces and values available
        for nskey, ns in self._namespaces.items():
            environment.globals[nskey] = ns
        environment.globals['values'] = self._values

        # Render template
        template = environment.get_template(name)
        render = template.render()

        return render


__all__ = [
    'Ninjecto',
]
