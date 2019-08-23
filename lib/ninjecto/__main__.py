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
Executable module entry point.
"""

from os import walk
from pathlib import Path
from logging import getLogger

from .core import Ninjecto
from .inputs import load_files
from .values import load_values


log = getLogger(__name__)


def main():
    from setproctitle import setproctitle
    setproctitle('ninjecto')

    # Parse arguments
    from .args import InvalidArguments, parse_args
    try:
        args = parse_args()
    except InvalidArguments:
        return 1

    # Load config
    if args.configs:
        log.info('Loading configuration files ...')
    config = load_files(args.configs)

    # Load values
    if args.values_files:
        log.info('Loading values files ...')
    values = load_values(args.values_files, args.values)

    # Execute engine

    # Single file rendering
    if args.input.is_file():
        ninjecto = Ninjecto(
            config, values,
            args.libraries,
            args.input, args.output,
        )
        ninjecto.run(args.dry_run, args.override)
        return 0

    # Directory - recursive rendering
    for root, folders, files in walk(str(args.input)):
        # str(input) as only 3.6+ supports passing Path

        subpath = Path(root).relative_to(args.input)

        for file in files:
            inputfile = args.input / subpath / file
            outputfile = args.output / subpath / file

            ninjecto = Ninjecto(
                config, values,
                args.libraries,
                inputfile, outputfile,
            )
            ninjecto.run(args.dry_run, args.override)

    return 0


if __name__ == '__main__':
    exit(main())


__all__ = []
