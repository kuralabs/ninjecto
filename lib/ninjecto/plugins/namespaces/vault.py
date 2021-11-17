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

from os import environ

from hvac import Client

from ...utils.dictionary import Namespace


def namespace_vault(config):
    """
    Fetch values stored on a Vault service.

    Vault is a service used to manage secrets and protect sensitive data. Check
    more information at https://www.vaultproject.io/

    :param dict config: Plugin configuration, if any.

    :return: A dynamic namespace to access a secret on any level of a Vault
    service.
    """
    return Namespace({
        config: Vault(
            token=environ.get(connection_data.pop('token_env')),
            **connection_data
        )
        for config, connection_data in config.configurations
    })


class VaultKV2:
    """
    Vault accessor for kv_v2 engines

    :param vault_client: Client connected to a vault instance.
    :param mount_point: Name of the engine on the vault instance.
    """
    def __init__(self, vault_client, mount_point):
        self._vault = vault_client
        self._mount_point = mount_point
        self._secrets = {}

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as e:
            raise AttributeError(e)

    def __getitem__(self, path):

        # The path is cached because of the "spatial locality" principle
        # it is probable that if one key/value is accesed the others will also
        # be requested, and since the vault call brings all key/values under
        # a path, we might as well store them
        if path not in self._secrets:
            self._secrets[path] = Namespace(
                self._vault.secrets.kv.v2.read_secret(
                    path,
                    mount_point=self._mount_point
                )['data']['data']
            )

        return self._secrets[path]


class Vault:
    """
    High level vault accessor holding instances of vault engines.

    :param url: Vault instance address.
    :param token: Access token for vault.
    :param engine_type: One of the support vault engines.
    """

    VAULT_ENGINES = {
        'kv_v2': VaultKV2
    }

    def __init__(self, url, token, engine_type='kv_v2'):
        if engine_type not in self.VAULT_ENGINES:
            raise Exception(f'Invalid or unsupported engine {engine_type}')

        self._vault = Client(url=url, token=token)
        self._engine_class = self.VAULT_ENGINES[engine_type]
        self._engines = {}

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as e:
            raise AttributeError(e)

    def __getitem__(self, engine_name):
        if engine_name not in self._engines:
            self._engines[engine_name] = self._engine_class(
                self._vault,
                engine_name
            )

        return self._engines[engine_name]


__all__ = [
    'namespace_vault'
]
