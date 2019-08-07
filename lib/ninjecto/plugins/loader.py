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
Module to load plugins.
"""

from copy import copy
from logging import getLogger
from collections import OrderedDict

from pkg_resources import iter_entry_points


log = getLogger(__name__)


class FunctionLoader(object):
    """
    Function loader utility class.

    This class allows to load functions using Python entry points.

    :param str component: Name of the component.
    :param str api_version: Version of the API.
    """

    _locally_registered = None

    def __init__(self, package, component, api_version='1.0'):
        super().__init__()

        self._package = package
        self._component = component
        self._api_version = api_version

        self.entrypoint = '{package}_plugins_{component}_{api_version}'.format(
            package=self._package,
            component=self._component,
            api_version=self._api_version.replace('.', '_'),
        )

        self._functions_cache = OrderedDict()

    def __call__(self, cache=True):
        return self.load_functions(cache=cache)

    @classmethod
    def register(cls, key):
        """
        Register a function locally.

        This method is expected to be used as a decorator. It allows to
        register a function locally without having to create a full Python
        package to use entrypoints.
        """

        def decorator(function):
            if not callable(function):
                raise ValueError(
                    '{} ({}) is not callable'.format(
                        function, key,
                    )
                )

            cls._locally_registered[key] = function
            return function

        return decorator

    @classmethod
    def unregister(cls, key):
        """
        Unregister a previously registered function.
        """
        if cls._locally_registered:
            del cls._locally_registered[key]

    @classmethod
    def reset(cls):
        """
        Reset locally registered functions.
        """
        if cls._locally_registered is None:
            cls._locally_registered = OrderedDict()
        cls._locally_registered.clear()

    def load_functions(self, cache=True):
        """
        Load all available functions.

        This function load all available functions by discovering installed
        functions registered in the entry point. This can be costly or error
        prone if the package that declared the entrypoint misbehave. Because of
        this a cache is stored after the first call.

        :param bool cache: If ``True`` return the cached result. If ``False``
         force reload of all functions registered for the entry point.

        :return: An ordered dictionary associating the name for which the
         function was registered and and the function itself.
        :rtype: OrderedDict
        """

        # Return cached value if call is repeated
        if cache and self._functions_cache:
            return copy(self._functions_cache)

        # Add built-in plugin types
        available = OrderedDict()

        # Iterate over entry points
        log.debug('Loading entrypoint {}'.format(self.entrypoint))

        for ep in iter_entry_points(group=self.entrypoint):

            name = ep.name

            try:
                function = ep.load()
            except Exception:
                log.exception(
                    'Unable to load function "{}"'.format(name)
                )
                continue

            if not callable(function):
                log.error(
                    'Ignoring function {} ({}) as it isn\'t callable'.format(
                        function, name,
                    )
                )
                continue

            available[name] = function
            log.debug(
                'Successfully loaded "{}" function {}'.format(
                    self._component, name,
                )
            )

        # Load locally registered
        available.update(
            self.__class__._locally_registered
        )

        # Save cache and return
        self._functions_cache = available
        return copy(self._functions_cache)


__all__ = [
    'FunctionLoader',
]
