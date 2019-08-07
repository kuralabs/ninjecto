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
Namespace plugin to access git context.
"""

from logging import getLogger
from collections import namedtuple

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


log = getLogger(__name__)


def namespace_git(config, filepath):
    """
    Fetch information relative to the git context where the file input file is
    located.

    :param dict config: Plugin configuration, if any.
    :param Path filepath: Path file been rendered.

    :return: A named tuple with information from git context.

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

    :rtype: namedtuple
    """

    parent = str(filepath.parent)
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
            value = finder(directory=parent)
        except GitError:
            log.exception('Failed fetching git {} property'.format(prop))
        except GitNotFound:
            pass
        context[prop] = value

    # Create git namespace object
    git_type = namedtuple('git', list(properties))
    git = git_type(**context)

    log.debug('git namespace: {}'.format(git))
    return git


__all__ = [
    'namespace_git',
]
