# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 KuraLabs S.R.L
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
Utilities for git repositories.
"""

from shutil import which
from logging import getLogger

from .command import run


log = getLogger(__name__)


class GitError(Exception):
    """
    Typed exception raised when a call to a git executable failed.
    """


class GitNotFound(Exception):
    """
    Typed exception raised when the git executable wasn't found on the system.
    """

    def __init__(self):
        super().__init__('Git executable not found in your system.')


def find_git():
    """
    Find the git executable.

    :return: Absolute path to the git executable.
    :rtype: str
    """
    git = which('git')
    if git is None:
        log.debug('Git executable not found in your system.')
        raise GitNotFound()
    return git


def find_tag(git=None, directory='.'):
    """
    Find the tag for the current revision.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: The name of the tag pointing to the current revision.
     Raises GitError if no tag is found.
    :rtype: str
    """
    if git is None:
        git = find_git()

    # Get current revision
    call = run([
        git, '-C', directory,
        'describe', '--tags', '--exact-match', 'HEAD'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git tag:\n{}'.format(
            call.stderr
        ))

    return call.stdout


def find_root(git=None, directory='.'):
    """
    Find the root of the git repository.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: Absolute path to root of the git repository.
    :rtype: str
    """
    if git is None:
        git = find_git()

    call = run([
        git, '-C', directory,
        'rev-parse', '--show-toplevel'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git repository root:\n{}'.format(
            call.stderr
        ))

    return call.stdout


def find_branch(git=None, directory='.'):
    """
    Find the current branch of the git repository.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: The name of the branch the git repository is currently on.
    :rtype: str
    """
    if git is None:
        git = find_git()

    # Get current branch
    call = run([
        git, '-C', directory,
        'rev-parse', '--abbrev-ref', 'HEAD'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git branch:\n{}'.format(
            call.stderr
        ))

    return call.stdout


def find_revision(git=None, directory='.'):
    """
    Find the current revision (short hash) of the git repository.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: The short version of the revision the git repository is currently
     on.
    :rtype: str
    """
    if git is None:
        git = find_git()

    # Get current revision
    call = run([
        git, '-C', directory,
        'rev-parse', '--short', '--verify', 'HEAD'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git revision:\n{}'.format(
            call.stderr
        ))

    return call.stdout


def find_name(git=None, directory='.'):
    """
    Find the name of the author of the current revision.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: The name of the author of the current revision.
    :rtype: str
    """
    if git is None:
        git = find_git()

    # Get current revision
    call = run([
        git, '-C', directory,
        'log', '-1', '--pretty=format:%an'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git author name:\n{}'.format(
            call.stderr
        ))

    return call.stdout


def find_email(git=None, directory='.'):
    """
    Find the email of the author of the current revision.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: The email of the author of the current revision.
    :rtype: str
    """
    if git is None:
        git = find_git()

    # Get current revision
    call = run([
        git, '-C', directory,
        'log', '-1', '--pretty=format:%ae'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git author email:\n{}'.format(
            call.stderr
        ))

    return call.stdout


def find_subject(git=None, directory='.'):
    """
    Find the commit message subject of current revision.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: The commit message subject of current revision.
    :rtype: str
    """
    if git is None:
        git = find_git()

    # Get current revision
    call = run([
        git, '-C', directory,
        'log', '-1', '--pretty=format:%s'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git commit subject:\n{}'.format(
            call.stderr
        ))

    return call.stdout


def find_body(git=None, directory='.'):
    """
    Find the commit message body of current revision.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: The commit message body of current revision.
    :rtype: str
    """
    if git is None:
        git = find_git()

    # Get current revision
    call = run([
        git, '-C', directory,
        'log', '-1', '--pretty=format:%b'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git commit body:\n{}'.format(
            call.stderr
        ))

    return call.stdout


def find_date(git=None, directory='.'):
    """
    Find the commit date in strict ISO 8601 format.

    :param str git: Path to git executable.
     If None, the default, will try to find it using :func:`find_git`.
    :param str directory: Run as if git was started in ``directory`` instead of
     the current working directory.

    :return: The commit date in strict ISO 8601 format.
    :rtype: str
    """
    if git is None:
        git = find_git()

    # Get current revision
    call = run([
        git, '-C', directory,
        'log', '-1', '--pretty=format:%aI'
    ])
    if call.returncode != 0:
        raise GitError('Unable to determine git commit date:\n{}'.format(
            call.stderr
        ))

    return call.stdout


__all__ = [
    'find_git',
    'find_tag',
    'find_root',
    'find_branch',
    'find_revision',
    'find_name',
    'find_email',
    'find_subject',
    'find_body',
    'find_date',
]
