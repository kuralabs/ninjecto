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
Basic test for Ninjecto.
"""

from pathlib import Path
from logging import getLogger
from ninjecto.core import Ninjecto
from yaml import safe_load as yaml_load


log = getLogger(__name__)


def test_basic():

    filename = "basic.yaml"
    template = filename + ".tpl"

    expected_result = {'basic': 'basic'}

    # Load the generic configuration
    generic_config = yaml_load(
        (Path(__file__).parent / "config" / "config.yaml").open("r")
    )
    templates_dir = Path(__file__).parent / "templates"
    output_path = templates_dir / filename

    _ninjecto = Ninjecto(
        config=generic_config,
        local=None,
        filters={},
        namespaces={},
        libraries=[],
        values={'basic_value': 'basic'},
        source=templates_dir / template,
        destination=templates_dir,
        filename=filename,
    )

    # Override in case the file already exists
    _ninjecto.run(override=True)

    result_dict = yaml_load(
        output_path.read_text(encoding="utf-8")
    )

    assert result_dict == expected_result

    # Clean up the generated file
    output_path.unlink(missing_ok=True)


def test_config():

    """
    Test for Ninjecto with a specific configuration.

    """

    log.info("Running test_nested...")

    filename = "brackets.yaml"
    template = filename + ".tpl"

    expected_result = {
        'helm': '{{ .Values.lab1.values }}',
    }

    # Load the generic configuration
    config = yaml_load(
        (
            Path(__file__).parent / "config" / "config_brackets.yaml"
        ).open("r")
    )
    templates_dir = Path(__file__).parent / "templates"
    output_path = templates_dir / filename

    _ninjecto = Ninjecto(
        config=config,
        local=None,
        filters={},
        namespaces={},
        libraries=[],
        values={
            'location': 'lab1',
        },
        source=templates_dir / template,
        destination=templates_dir,
        filename=filename,
    )

    # Override in case the file already exists
    _ninjecto.run(override=True)

    result_dict = yaml_load(
        output_path.read_text(encoding="utf-8")
    )

    assert result_dict == expected_result

    # Clean up the generated file
    output_path.unlink(missing_ok=True)


def test_nested():

    """
    Test for nested values in Ninjecto.

    This test checks if the Ninjecto can correctly resolve nested values
    from the configuration and templates.

    Dynamic values " values.location " in the template:
        server1: {{ values[ values.location ].config.ssh }}

    Ninjecto will resolve the nested value of `values.location`

    Static values "lab2" in the template:
        server2: {{ values["lab2"].config.ssh }}
    """

    log.info("Running test_nested...")

    filename = "nested.yaml"
    template = filename + ".tpl"

    expected_result = {
        'server1': 'key1',
        'server2': 'key2',
    }

    # Load the generic configuration
    generic_config = yaml_load(
        (Path(__file__).parent / "config" / "config.yaml").open("r")
    )
    templates_dir = Path(__file__).parent / "templates"
    output_path = templates_dir / filename

    _ninjecto = Ninjecto(
        config=generic_config,
        local=None,
        filters={},
        namespaces={},
        libraries=[],
        values={
            'location': 'lab1',
            'lab1': {
                'config': {
                    'ssh': 'key1',
                },
            },
            'lab2': {
                'config': {
                    'ssh': 'key2',
                },
            },
        },
        source=templates_dir / template,
        destination=templates_dir,
        filename=filename,
    )

    # Override in case the file already exists
    _ninjecto.run(override=True)

    result_dict = yaml_load(
        output_path.read_text(encoding="utf-8")
    )

    assert result_dict == expected_result

    # Clean up the generated file
    output_path.unlink(missing_ok=True)
