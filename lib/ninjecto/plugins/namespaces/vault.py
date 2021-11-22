# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 KuraLabs S.R.L
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
Namespace plugin to access secrets in a Vault instance.
"""

from os import environ
from logging import getLogger

from ...utils.dictionary import Namespace


log = getLogger(__name__)


def namespace_vault(config):
    """
    Fetch values stored on a Vault service.

    Vault is a service used to manage secrets and protect sensitive data.
    Check more information at https://www.vaultproject.io/

    To use this namespace add a configuration for your Vault instance of the
    form:

    .. code-block: toml

        [ninjecto.namespace.vault.configurations.myvault]
        url = 'https://myvault.domain.com/'
        token_env = 'NINJECTO_MYVAULT_TOKEN'

    Then, in the templates, use the namespace as::

        {{ vault.myvault.myengine.mysecret.mykey }}


    :param dict config: Plugin configuration, if any.

    :return: A dynamic namespace to access a secret on any level of a Vault
     service.
    :rtype: Namespace
    """

    if not hasattr(config, 'configurations'):
        log.info('Vault plugin has no configurations. Skipping setup.')
        return Namespace({})

    try:
        from hvac import Client
    except ImportError as e:
        log.critical(
            'Unable to import the Vault client. '
            'The package "hvac" is missing. '
            'Install ninjecto with the "vault" option as follows: '
            'pip3 install ninjecto[vault]'
        )
        raise e

    configs = {}

    log.info('Found Vault configurations: {}'.format(
        ', '.join(
            repr(confname)
            for confname, options
            in config.configurations)
    ))

    for confname, options in config.configurations:

        log.info(f'Loading Vault configuration {confname!r} ...')
        for option in ['url', 'token_env']:
            assert option in options, (
                f'{option!r} is missing in Vault configuration {confname!r}'
            )

        token = environ.get(options.pop('token_env'))
        if token is None:
            log.warning(
                'Environment variable {token_env!r} required by Vault '
                'configuration {confname!r} is UNSET!'
            )

        configs[confname] = Vault(
            confname,
            Client(token=token, **options)
        )

    return Namespace(configs)


class VaultKV2:
    """
    Vault accessor for kv_v2 engines.

    :param client: Client connected to a Vault instance.
    :param mount_point: Name of the engine on the vault instance.
    """

    def __init__(self, client, mount_point):
        self._client = client
        self._mount_point = mount_point
        self._secrets = {}

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as e:
            raise AttributeError(e)

    def __getitem__(self, path):

        # The path is cached because of the "spatial locality" principle
        # it is probable that if one key/value is accessed the others will also
        # be requested, and since the vault call brings all key/values under
        # a path, we might as well store them
        if path not in self._secrets:
            self._secrets[path] = Namespace(
                self._client.secrets.kv.v2.read_secret(
                    path,
                    mount_point=self._mount_point
                )['data']['data']
            )

        return self._secrets[path]


class Vault:
    """
    High level Vault accessor holding and client instance.

    :param str name: Name of the Vault configuration.
    :param client: Client connected to a Vault instance.
    """

    VAULT_ENGINES = {
        'kv_v2': VaultKV2,
    }

    def __init__(self, name, client):
        self._name = name
        self._client = client
        self._mounted = None
        self._engines = {}

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as e:
            raise AttributeError(e)

    def __getitem__(self, engine_name):

        # Fetch list of mounted engines
        if self._mounted is None:
            log.info(
                'Loading mounted secrets engines for Vault configuration '
                f'{self._name!r} ...'
            )
            self._mounted = \
                self._client.sys.list_mounted_secrets_engines()['data']

        # Fetch cached instance of the engine class
        if engine_name not in self._engines:
            path = f'{engine_name}/'

            # Check the mount exists
            if path not in self._mounted:
                raise RuntimeError(
                    f'Unknown mounted secret engine {engine_name!r}'
                )
            mountconf = self._mounted[path]

            # Determine engine type
            type_ = mountconf['type']
            if type_ == 'kv':
                version = mountconf['options']['version']
                type_ = f'{type_}_v{version}'

            # Check engine is supported
            if type_ not in self.VAULT_ENGINES:
                supported = ', '.join(sorted(self.VAULT_ENGINES.keys()))
                raise RuntimeError(
                    f'Mount {engine_name!r} is an unsupported engine '
                    f'type {type_!r}. Supported engines are: {supported}.'
                )

            # Instance engine class
            engine_class = self.VAULT_ENGINES[type_]
            self._engines[engine_name] = engine_class(
                self._client,
                engine_name,
            )

        return self._engines[engine_name]


__all__ = [
    'namespace_vault'
]
