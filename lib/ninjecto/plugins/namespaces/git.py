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
Namespace plugin to access git context.
"""

from logging import getLogger
from traceback import format_exc

from ...utils.git import (
    GitNotFound,
    GitError,
    find_tag,
    find_root,
    find_branch,
    find_revision,
    find_name,
    find_email,
    find_subject,
    find_body,
    find_date,
)
from ...utils.dictionary import Namespace


log = getLogger(__name__)


def namespace_git(config):
    """
    Fetch information relative to the git context.

    This function will fetch the git information only once per root directory
    unless the config function ``ninjecto.namespace.git.submodules`` is set to
    True, in which case the information will be called for every directory.

    :param dict config: Plugin configuration, if any.

    :return: A dynamic namespace function that returns an object with
     information from the git context of the file input it is called with.

     Values available:

     - ``tag``: tag for the current revision.
     - ``root``: root of the git repository.
     - ``branch``: current branch of the git repository.
     - ``revision``: current revision of the git repository.
     - ``name``: name of the author of the current revision.
     - ``email``: email of the author of the current revision.
     - ``subject``: commit message subject of current revision.
     - ``body``: commit message body of current revision.
     - ``date``: commit date in strict ISO 8601 format.

    :rtype: function
    """

    root = None
    cache = None

    def namespace(filepath):
        """
        Git dynamic namespace.

        :param Path filepath: Path file been rendered.

        :return: An object with information from the git context of the file
         input it is called with.
        :rtype: Namespace
        """
        nonlocal root
        nonlocal cache

        # Only consider directories
        if not filepath.is_dir():
            filepath = filepath.parent

        # If the root isn't set, set it
        if root is None:
            root = filepath

        # If the filepath is the same as the root, return the cache if
        # available. This is particularly useful for all files inside the
        # same directory
        if cache is not None and filepath == root:
            return cache

        # Check if the directory is a subdirectory of the root
        # If not, reset the root and clear the cache
        try:
            filepath.relative_to(root)
        except ValueError:
            root = filepath
            cache = None

        # If the submodule option is not enabled, return the cache if
        # available. In case the current directory is not a subpath of the
        # root, the cache was cleared and then this shouldn't execute.
        if cache is not None and not config.submodules:
            return cache

        context = {}

        # Try to determine git namespace
        properties = {
            'tag': find_tag,
            'root': find_root,
            'branch': find_branch,
            'revision': find_revision,
            'name': find_name,
            'email': find_email,
            'subject': find_subject,
            'body': find_body,
            'date': find_date,
        }
        for prop, finder in properties.items():
            value = None
            try:
                value = finder(directory=str(filepath))
            except GitError:
                log.debug(
                    'Failed fetching git {} property:\n{}'.format(
                        prop, format_exc(),
                    )
                )
            except GitNotFound:
                pass
            context[prop] = value

        # Create git namespace object
        git = Namespace(context)
        log.debug('git namespace: ({})'.format(
            ', '.join(sorted(context))
        ))

        cache = git
        return git

    return namespace


__all__ = [
    'namespace_git',
]
