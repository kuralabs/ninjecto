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

from .core import Ninjecto
from .values import load_values


def main():
    from setproctitle import setproctitle
    setproctitle('ninjecto')

    from .args import InvalidArguments, parse_args
    try:
        args = parse_args()
    except InvalidArguments:
        exit(1)

    values = load_values(args.values_files, args.values)
    ninjecto = Ninjecto(values, args.input, args.output)
    ninjecto.run(args.dry_run, args.override)

    exit(0)


if __name__ == '__main__':
    main()


__all__ = []
