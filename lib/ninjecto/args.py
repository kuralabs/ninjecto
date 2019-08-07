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
Argument management module.
"""

from pathlib import Path
from collections import OrderedDict
from argparse import Action, ArgumentParser
from logging import (
    ERROR, WARNING, DEBUG, INFO,
    StreamHandler, getLogger, Formatter, basicConfig,
)

from colorlog import ColoredFormatter

from . import __version__
from .utils.types import autocast


log = getLogger(__name__)


COLOR_FORMAT = (
    '  {thin_white}{asctime}{reset} | '
    '{log_color}{levelname:8}{reset} | '
    '{log_color}{message}{reset}'
)
SIMPLE_FORMAT = (
    '  {asctime} | '
    '{levelname:8} | '
    '{message}'
)
LEVELS = {
    0: ERROR,
    1: WARNING,
    2: INFO,
    3: DEBUG,
}


class InvalidArguments(Exception):
    """
    Typed exception that allows to fail in argument parsing and verification
    without quiting the process.
    """
    pass


class ExtendAction(Action):
    """
    Action that allows to combine nargs='+' with the action='append' behavior
    but generating a flat list.

    This allow to specify in a argument parser class an action that allows
    to specify multiple values per argument and multiple arguments.

    Usage::

        parser = ArgumentParser(...)
        parser.register('action', 'extend', ExtendAction)

        parser.add_argument(
            '-o', '--option',
            nargs='+',
            dest='options',
            action='extend',
            help='Some description'
        )

    Then, in CLI::

        executable --option var1=var1 var2=var2 --option var3=var3

    And this generates a::

        Namespace(options=['var1=var1', 'var2=var2', 'var3=var3'])
    """

    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest) or []
        items.extend(values)
        setattr(namespace, self.dest, items)


def validate_args(args):
    """
    Validate that arguments are valid.

    :param args: An arguments namespace.
    :type args: :py:class:`argparse.Namespace`

    :return: The validated namespace.
    :rtype: :py:class:`argparse.Namespace`
    """

    # Setup logging
    level = LEVELS.get(args.verbosity, DEBUG)

    if not args.colorize:
        formatter = Formatter(
            fmt=SIMPLE_FORMAT, style='{'
        )
    else:
        formatter = ColoredFormatter(
            fmt=COLOR_FORMAT, style='{'
        )

    handler = StreamHandler()
    handler.setFormatter(formatter)

    basicConfig(
        handlers=[handler],
        level=level,
    )

    log.debug('Arguments:\n{}'.format(args))

    # Check if configuration exists
    if args.config:
        args.config = Path(args.config)

        if not args.config.is_file():
            raise InvalidArguments(
                'No such configuration file {}'.format(args.config)
            )

        args.config = args.config.resolve()

    # Check if input exists
    args.input = Path(args.input)

    if not args.input.exists():
        raise InvalidArguments(
            'No such file or directory {}'.format(args.input)
        )

    args.input = args.input.resolve()

    # Check if output exists
    args.output = Path(args.output)

    if args.output.exists() and not args.override:
        raise InvalidArguments(
            'Output file or directory {} exists. '
            'Use --override to force overriding.'
        )

    args.output = args.output.resolve()

    # Check values files
    if args.values_files:
        args.values_files = [
            Path(values_file)
            for values_file in args.values_files
        ]

        missing = [
            values_file
            for values_file in args.values_files
            if not values_file.is_file()
        ]
        if missing:
            raise InvalidArguments(
                'No such files {}'.format(', '.join(map(str, missing)))
            )

        args.values_files = [
            values_file.resolve()
            for values_file in args.values_files
        ]

    # Check values options
    if args.values:
        values = OrderedDict()

        for pair in args.values:

            if '=' not in pair:
                raise InvalidArguments(
                    'Invalid value "{}"'.format(pair)
                )

            key, value = pair.split('=', 1)
            values[key] = autocast(value)

        args.values = values

    return args


def parse_args(argv=None):
    """
    Argument parsing routine.

    :param argv: A list of argument strings.
    :type argv: list

    :return: A parsed and verified arguments namespace.
    :rtype: :py:class:`argparse.Namespace`
    """

    parser = ArgumentParser(
        description=(
            'Ninjecto - Ninja Injection Tool'
        )
    )
    parser.register('action', 'extend', ExtendAction)

    # Standard options
    parser.add_argument(
        '-v', '--verbose',
        help='Increase verbosity level',
        dest='verbosity',
        default=0,
        action='count'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='{} {}'.format(
            parser.description,
            __version__,
        ),
    )
    parser.add_argument(
        '--no-color',
        dest='colorize',
        action='store_false',
        help='Do not colorize the log output'
    )

    # Configuration
    parser.add_argument(
        '-c', '--config',
        dest='config',
        help=(
            'Ninjecto and plugins configuration file. '
            'Must be a .toml, .yaml or .json'
        ),
    )

    # Dry run
    parser.add_argument(
        '-d', '--dry-run',
        help='Dry run the pipeline',
        default=False,
        action='store_true'
    )

    # Values
    parser.add_argument(
        '-a', '--values',
        nargs='+',
        action='extend',
        metavar='KEY=VALUE',
        help='Values to render inputs with'
    )
    parser.add_argument(
        '-f', '--values-file',
        dest='values_files',
        action='append',
        metavar='VALUES_FILE',
        help=(
            'One or more paths to files with values to render inputs with. '
            'Must be a .toml, .yaml or .json'
        ),
    )

    # Input and outputs
    parser.add_argument(
        '-o', '--override',
        help='Override existing files',
        default=False,
        action='store_true'
    )
    parser.add_argument(
        'input',
        help='File or directory to render'
    )
    parser.add_argument(
        'output',
        help='File or directory to write to'
    )

    # Parse and validate arguments
    args = parser.parse_args(argv)

    try:
        args = validate_args(args)
    except InvalidArguments as e:
        log.critical(e)
        raise e

    return args


__all__ = [
    'parse_args',
]
