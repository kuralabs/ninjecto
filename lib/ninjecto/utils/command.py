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
Utilities for calling commands.

Why this module exists?

A/ Because subprocess.run didn't exists until Python 3.5, and it became useful
   until 3.6 where we could specify the encodings.

   https://docs.python.org/3/library/subprocess.html#subprocess.run

   This module pre-dates these versions, and offer a similar interface.
"""

from logging import getLogger
from traceback import format_exc
from shlex import split as shsplit
from collections import namedtuple
from subprocess import Popen, PIPE, DEVNULL


log = getLogger(__name__)


CompletedProcess = namedtuple(
    'CompletedProcess',
    ['args', 'stdout', 'stderr', 'returncode']
)


def run(command):
    """
    Run the command described by args. Safely wait for command to complete,
    then return a CompletedProcess instance.

    :param command: Command to run.
    :type command: list or str

    :return: namedtuple with the following attributes:

    - ``args``: Arguments describing the command to execute.
    - ``stdout``: Standard output of the command as UTF-8.
    - ``stderr``: Standard error of the command as UTF-8.
    - ``returncode``: Return code of the command.

    :rtype: CompletedProcess
    """
    if isinstance(command, str):
        command = shsplit(command)

    try:
        process = Popen(
            command,
            stdin=DEVNULL,
            stderr=PIPE,
            stdout=PIPE,
            env={'LC_ALL': 'C', 'LANG': 'C'}
        )
        stdout, stderr = process.communicate()

    except OSError:  # E.g. command not found
        log.critical(format_exc())
        raise

    return CompletedProcess(
        args=command,
        stdout=stdout.decode('utf-8').strip(),
        stderr=stderr.decode('utf-8').strip(),
        returncode=process.returncode,
    )


__all__ = [
    'run',
]
