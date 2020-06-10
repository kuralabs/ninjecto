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

    # Check output flag semantics
    # XXX: Maybe use a Default class
    if args.output and args.output_in:
        raise InvalidArguments('Either use --output or --output-in')
    if args.output is None and args.output_in is None:
        args.output = True

    # Check if source exists
    args.source = Path(args.source)

    if not args.source.exists():
        raise InvalidArguments(
            'No such input file or directory: "{}"'.format(args.source)
        )

    args.source = args.source.resolve()

    # Check destination
    args.destination = Path(args.destination)

    if args.destination.exists():
        if args.output and not args.override:
            raise InvalidArguments(
                'Output file or directory "{}" exists. '
                'Use --force to force overriding.'.format(
                    str(args.destination),
                )
            )
        elif args.output_in and not args.destination.is_dir():
            raise InvalidArguments(
                'Output must be a directory when using --output-in.'
            )
    elif args.output_in:
        if not args.parents:
            raise InvalidArguments(
                'No such output directory "{}" exists. '
                'Use --parents to create it.'.format(
                    str(args.destination),
                )
            )

        args.destination.mkdir(parents=True)

    args.destination = args.destination.resolve()

    # Check if files and directories exists
    for human, argsattr, checker in [
        ('configurations', 'configs', lambda path: path.is_file()),
        ('libraries', 'libraries', lambda path: path.is_dir()),
        ('values files', 'values_files', lambda path: path.is_file()),
    ]:
        assert hasattr(args, argsattr)
        files = getattr(args, argsattr)
        if not files:
            continue

        files = [
            Path(file)
            for file in files
        ]

        # Check if exists
        missing = [
            file
            for file in files
            if not file.exists()
        ]
        if missing:
            raise InvalidArguments(
                'No such {}: {}'.format(
                    human,
                    ', '.join(map(str, missing)),
                )
            )

        # Check if valid
        invalid = [
            file
            for file in files
            if not checker(file)
        ]
        if invalid:
            raise InvalidArguments(
                'Invalid {} {}'.format(
                    human,
                    ', '.join(map(str, invalid)),
                )
            )

        files = [
            file.resolve()
            for file in files
        ]

        setattr(args, argsattr, files)

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
        action='count',
        dest='verbosity',
        default=0,
        help='Increase verbosity level',
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
        action='store_false',
        dest='colorize',
        help='Do not colorize the log output'
    )

    # Configuration
    parser.add_argument(
        '-c', '--config',
        action='append',
        dest='configs',
        default=[],
        help=(
            'Ninjecto and plugins configuration files. '
            'Must be a .toml, .yaml or .json. '
            'All files are parsed and merged left to right.'
        ),
    )

    # Templates libraries
    parser.add_argument(
        '-l', '--library',
        action='append',
        dest='libraries',
        default=[],
        help=(
            'One or more paths to directories with a templates library. '
            'A library allows to inherit, import and other advanced '
            'templating features. All path are made available, load priority '
            'is left to right.'
        ),
    )

    # Dry run
    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        default=False,
        help='Dry run the pipeline',
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
        '-u', '--values-file',
        action='append',
        dest='values_files',
        default=[],
        metavar='VALUES_FILE',
        help=(
            'One or more paths to files with values to render inputs with. '
            'Must be a .toml, .yaml or .json'
        ),
    )

    # Input and outputs
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        dest='override',
        default=False,
        help='Override existing files',
    )
    parser.add_argument(
        '-r', '--levels',
        type=int,
        default=None,
        help='Limit recursion for directories to this number of levels',
    )

    parser.add_argument(
        '-o', '--output',
        action='store_true',
        default=None,
        help='Write generated file or directory to OUTPUT',
    )
    parser.add_argument(
        '-i', '--output-in',
        action='store_true',
        default=None,
        help='Write generated files in the OUTPUT directory',
    )
    parser.add_argument(
        '-p', '--parents',
        action='store_true',
        default=False,
        help='Create directory and its parents when using --output-in mode',
    )

    parser.add_argument(
        'source',
        metavar='SRC',
        help='File or directory to render',
    )
    parser.add_argument(
        'destination',
        metavar='DST',
        help='File or directory to write to',
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
