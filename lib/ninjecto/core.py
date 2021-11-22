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
Core module.
"""

from logging import getLogger
from collections import OrderedDict

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
    """
    Ninjecto Core Class.

    Provides an API to render a directory tree, a single file, or arbitrary
    content.

    :param dict config: Configuration tree.
     Use ``ninjecto.config.load_config`` to get a normalized data structure.
    :param module local: Loaded ninjeconf.py Python module. Currently unused.
    :param OrderedDict filters: Dictionary mapping the name of the filter and
     the function implementing it.
    :param OrderedDict namespaces: Dictionary mapping the name of the namespace
     and the function implementing it.
    :param list libraries: List of Paths to user libraries directories.
    :param dict values: Arbitrary tree of values to pass to the templates.
    :param Path source: Source filepath. Either a file or a directory.
    :param Path destination: Destination filepath. Either a file or a
     directory.
    :param str filename: Override the destination filename.
     Pass None to use the rendered name.
    """

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

        # Instance namespaces
        self._namespaces = OrderedDict()
        for nskey, ns in namespaces.items():
            nsconf = getattr(
                self._config.ninjecto.namespace, nskey, Namespace()
            )
            self._namespaces[nskey] = ns(nsconf)

        self._libraries = libraries

        self._values = values
        self._source = source
        self._destination = destination
        self._filename = filename

        self._dry_run = False
        self._override = False
        self._levels = None

        self.undefmap = {
            'Undefined': Undefined,
            'ChainableUndefined': ChainableUndefined,
            'DebugUndefined': DebugUndefined,
            'StrictUndefined': StrictUndefined,
        }

    def run(self, dry_run=False, override=False, levels=None):
        """
        Execute the rendering of this Ninjecto context.

        :param bool dry_run: Execute rendering without writing any file.
        :param bool override: Override files if exit.
        :param int levels: Maximum numbers of directories levels to recurse
         into.

        :return: Number of files processed.
        :rtype: int
        """

        log.info('Render {} -> {}'.format(self._source, self._destination))
        if self._values:
            log.info('With values:\n{}'.format(self._values))

        log.info(
            'Using filters: {}'.format(', '.join(self._filters.keys()))
        )
        log.info(
            'Using namespaces: {}'.format(', '.join(self._namespaces.keys()))
        )

        self._dry_run = dry_run
        self._override = override
        self._levels = levels
        return self.process(
            self._source,
            self._destination,
            self._filename,
            self._levels,
        )

    def process(self, src, dstdir, filename=None, levels=None):
        """
        Process a path.

        Path can be a single file, or a directory, in which case it will
        recurse into it.

        :param Path src: Path to the source file or directory.
        :param Path disdir: Path to the destination directory.
        :param str filename: Override the destination filename.
         Pass None to use the rendered name.
        :param int levels: Maximum numbers of directories levels to recurse
         into.

        :return: Number of files processed.
        :rtype: int
        """

        config = self._config.ninjecto
        dry_run = self._dry_run
        override = self._override

        if levels is not None and levels < 1:
            return 0

        # First thing first, render the filename
        if filename is None:
            filename = self.render(
                src.name,
                src.name,
                filepath=src,
            )

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
                src.read_text(encoding=config.input.encoding),
                filepath=src,
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
                processed += self.process(
                    subfile, dst,
                    filename=None,
                    levels=levels,
                )

            return processed

        raise RuntimeError(
            '{} isn\'t a file nor directory. '
            'Don\'t know what to do.'.format(src)
        )

    def render(self, name, content, filepath=None):
        """
        Render a template.

        :param str name: Name of the template.
         Used as key to fetch the template only.
        :param str content: The content of the template itself.
        :param Path filepath: Path to the template file, if any.
         This is used to call namespaces that depend on the filepath.
         Namespaces that require a filepath won't be called if unset.

        :return: The rendered template.
        :rtype: str
        """

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
                }, delimiter=config.prefixloader.delimiter),
            ]),
        })
        environment = Environment(**envconf)

        # Make filters available
        for key, fltr in self._filters.items():
            environment.filters[key] = fltr

        # Make namespaces and values available
        for nskey, ns in self._namespaces.items():
            if callable(ns) and filepath:
                environment.globals[nskey] = ns(filepath)
                continue
            environment.globals[nskey] = ns

        environment.globals['values'] = self._values

        # Render template
        template = environment.get_template(name)
        render = template.render()

        return render


__all__ = [
    'Ninjecto',
]
