.. image:: https://github.com/kuralabs/ninjecto/blob/6f58c7ece71a4e9fcb534582f97fb931babecb67/doc/ninjecto.png
   :alt: Ninjecto - Ninja Injection Tool
   :width: 300px
   :align: center

========
Ninjecto
========

.. image:: https://img.shields.io/pypi/v/ninjecto
   :target: https://pypi.org/project/ninjecto/
   :alt: PyPI

.. image:: https://img.shields.io/github/license/kuralabs/ninjecto
   :target: https://choosealicense.com/licenses/apache-2.0/
   :alt: License

**Ninjecto - Ninja Injection Tool** - A sophisticated template processing and
configuration management tool that combines the power of Jinja2 templating with
hierarchical configuration management and an extensible plugin system.

Ninjecto enables you to recursively generate dynamic content from templates
using structured configuration data, with support for multiple input formats,
custom filters and environment-aware namespaces.

.. contents::
   :local:
   :depth: 2


Key Features
============

🎯 **Powerful Template Engine**
   Built on Jinja2 with full support for template inheritance, macros, and
   advanced templating features.

⚙️ **Hierarchical Configuration**
   Intelligent configuration loading from system, user, project, and custom
   sources with automatic merging.

🔌 **Extensible Plugin System**
   Custom filters and namespaces with built-in support for environment
   variables, git context, and HashiCorp Vault.

📁 **Multi-Format Support**
   Process single files or entire directory trees with support for YAML, JSON,
   and TOML configuration files

🌍 **Environment Integration**
   Access environment variables, git repository information, and external
   services directly in templates.

🛡️ **Production Ready**
   Robust error handling, dry-run mode, and configurable undefined variable
   behavior.


Use Cases
=========

Ninjecto is the swiss-army knife for template rendering and configuration
management, suitable for a wide range of use cases from simple file generation
to complex project scaffolding and automation tasks, like:

- Generating configuration files for applications and services. For example,
  generating Kubernetes manifests, Docker Compose files, or application config
  files from templates and structured data.
- Scaffolding project structures with dynamic content based on user-defined
  templates and configuration. For example creating a company specific template
  to start a new microservice or language specific application project.
- Automating repetitive tasks that involve generating text files with dynamic
  content.
- Any other task that requires dynamic text generation based on structured
  data, for example generating documentation, reports, or code snippets.
- To generate static websites with dynamic content based on templates and data.
- To manage infrastructure as code (IaC) templates, such as Terraform or
  Ansible, by generating configuration files based on environment-specific
  data.


Quick Start
===========

Installation
------------

Install ninjecto using your package manager, for example for uv:

.. code-block:: bash

   uv tool install ninjecto

For HashiCorp Vault support:

.. code-block:: bash

   uv tool install ninjecto[vault]

Basic Usage
-----------

Create a simple template file:

.. code-block:: jinja

   # config.yml.tpl
   app_name: {{ values.app_name }}
   version: {{ values.version }}
   environment: {{ env.ENVIRONMENT | default('development') }}

   # Git information
   repository: {{ git.root }}
   commit: {{ git.revision }}
   branch: {{ git.branch }}

Create a values file:

.. code-block:: yaml

   # values.yaml
   app_name: "my-application"
   version: "1.0.0"

Render the template:

.. code-block:: bash

   ninjecto -u values.yaml config.yml.tpl config.yml


Core Concepts
=============

Templates
---------

Ninjecto uses Jinja2 templating engine with additional filters and namespaces.
Templates can be single files or entire directory structures that get processed
recursively. You may even use conditionals in filenames or directory names to
control which files are rendered, based on values or environment context.
This enables dynamic file generation and flexible project scaffolding.

Values and Configuration
------------------------

Values are provided through multiple sources with a clear hierarchy:

#. Command-line values (``-a key.subkey=value``)
#. Values files (``-u values.yaml``)
#. Standard input (``--values-in yaml``)

Configuration follows a hierarchical loading system:

#. Package default configuration
#. System configuration (``/etc/ninjecto/config.*``)
#. User configuration (``$XDG_CONFIG_HOME/ninjecto/config.*``)
#. User alternative configuration (``$HOME/.ninjerc.*``)
#. Project configuration (``<gitroot>/.ninjerc.*``)
#. Local configuration (``$PWD/.ninjerc.*``)
#. Explicit configuration files (``-c config.yaml``)

Namespaces
----------

Namespaces provide access to external data sources. They are implemented as
plugins and can be used in templates to fetch dynamic data.

Ninjecto includes several built-in namespaces:

- **env**: Environment variables with safe name filtering
- **git**: Git repository information, specifically:
  - ``tag``: tag for the current revision.
  - ``root``: root of the git repository.
  - ``branch``: current branch of the git repository.
  - ``revision``: current revision of the git repository.
  - ``name``: name of the author of the current revision.
  - ``email``: email of the author of the current revision.
  - ``subject``: commit message subject of current revision.
  - ``body``: commit message body of current revision.
  - ``date``: commit date in strict ISO 8601 format.
- **vault**: HashiCorp Vault secrets (requires vault extra)

You may implement additional namespaces as needed using the plugin system.

Filters
-------

Filter are Python functions that can be registered and then used in your
templates. They can accept multiple arguments and return, usually, a string to
be place in the rendered output, or passed down to other filters.

You may implement as many filters as you need using the plugin system.

Ninjecto includes several powerful built-in filters:

**Text Processing:**
- ``comment``: Add language-specific comments
- ``quote``: Add quotes with proper escaping
- ``read``: Read content from external files

**String Transformation (via Inflection package):**
- ``camelize``, ``dasherize``, ``humanize``
- ``pluralize``, ``singularize``
- ``underscore``, ``titleize``

Libraries
---------

Libraries are directories containing reusable macros and reusable templates
(for template inheritance) that can be imported into your main templates.

Macros are reusable template snippets that promotes DRY (Don't Repeat Yourself)
principles and modular template design.

Template inheritance allows you to define base templates with common structure
and extend them in child templates, overriding specific blocks as needed.

You may implement as many libraries as you need, see below for more details.


Usage Examples
==============

Process Directory Trees
------------------------

.. code-block:: bash

   # Process entire directory with templates
   ninjecto -u values.yaml templates/ output/

   # Limit recursion depth
   ninjecto -r 2 -u values.yaml templates/ output/

Using Filters
-------------

.. code-block:: jinja

   # Comment filter for different languages
   {{ "TODO: Implement feature" | comment('python') }}
   # Result: # TODO: Implement feature

   {{ "Configuration block" | comment('html') }}
   # Result: <!-- Configuration block -->

   # Quote filter
   {{ message | quote('"') }}

   # Read external files
   {{ 'VERSION' | read }}

   # Inflection filters
   {{ 'user_name' | camelize }}  # Result: userName
   {{ 'blog_post' | pluralize }}  # Result: blog_posts

Environment Integration
-----------------------

.. code-block:: jinja

   # Access environment variables safely
   database_url: {{ env.DATABASE_URL }}
   debug_mode: {{ env.DEBUG | default('false') }}

   # Git repository context
   build_info:
     commit: {{ git.revision }}
     branch: {{ git.branch }}
     author: {{ git.name }} <{{ git.email }}>
     date: {{ git.date }}

Conditional File Creation
-------------------------

.. code-block:: bash

   $ ls
   {% if values.docker %}.dockerignore{% endif %}
   {% if values.docker %}Dockerfile{% endif %}


Plugin System
=============

Filters
-------

Create a ``ninjeconf.py`` in the root where you run Ninjecto. This file will be
automatically loaded and any filter registered there will be available in your
templates.

To create a filter, use the ``register`` decorator from
``ninjecto.plugins.filters``:

.. code-block:: python

   from ninjecto.plugins import filters

   @filters.register('uppercase')
   def uppercase_filter(value):
       return str(value).upper()

   @filters.register('format_currency')
   def format_currency(amount, currency='USD'):
       return f"{amount:.2f} {currency}"

You may now use your filters in your templates:

.. code-block:: jinja

   {{ "hello world" | uppercase }}  # Result: HELLO WORLD
   {{ 1234.5 | format_currency('EUR') }}  # Result: 1234.50 EUR

If you want to distribute your filters as a package, you can create an entry
point in your ``setup.py`` or ``pyproject.toml``:

.. code-block:: python

   setup(
       ...
       entry_points={
           'ninjecto_plugins_filters_1_0': [
               'my_filter = my_package.my_module:my_filter',
           ],
       },
       ...
   )

Namespaces
----------

Similar to filters, you can create custom namespaces by creating a function
in your ``ninjeconf.py`` and registering it with the ``register`` decorator
from ``ninjecto.plugins.namespaces``:

.. code-block:: python

   from ninjecto.plugins import namespaces

   @namespaces.register('my_namespace')
   def my_namespace(config):
       return {
           'key1': config.get('value1', 'default1'),
           'key2': config.get('value2', 'default2'),
       }

The function receives the configuration specific to this namespace, as defined
in your configuration files. For example:

.. code-block:: toml

   [ninjecto.namespace.my_namespace]
   value1 = "value1"
   value2 = "value2"

You may now use your namespace in your templates:

.. code-block:: jinja

   {{ my_namespace.key1 }}  # Result: value1
   {{ my_namespace.key2 }}  # Result: value2

In this example, the namespace implementation in very simple, just returning
some static values. But you can implement any logic you need, including
accessing external services, reading files, etc. Check the built-in
``env``, ``git`` and ``vault`` namespaces for more complex examples on how
to retrieve dynamic data based on the environment or external systems.

If you want to distribute your namespaces as a package, you can create an entry
point in your ``setup.py`` or ``pyproject.toml``:

.. code-block:: python

   setup(
       ...
       entry_points={
           'ninjecto_plugins_namespaces_1_0': [
               'my_namespace = my_package.my_module:my_namespace',
           ],
       },
       ...
   )


Libraries
=========

To create a library, simply create a directory and place your macro templates
and base templates for inheritance. A good practice is to create a subdirectory
for macros and another for base templates, but this is not necessary if you
don't need to or have a different organization system. For example:

.. code-block:: text

   my_library/
   ├── macros/
   │   ├── config_macros.j2
   │   ├── string_macros.j2
   │   └── file_macros.j2
   └── base/
       └── base_template.tpl

You can specify as many libraries as needed using the ``-l`` or ``--library``
option.

Please note that file extensions are arbitrary and not mandatory, but it's a
good practice to use ``.j2`` or ``.jinja`` for macro files, and ``.tpl`` for
templates, and even better if your template is in a particular language, use
something like ``.yaml.tpl``, ``.json.tpl``, ``.html.tpl``, etc.

Macros
------

A macro is defined using the ``macro`` directive and can accept parameters.
For more information, see the Jinja2 documentation:

https://jinja.palletsprojects.com/en/latest/templates/#macros

Here is a basic example of a Jinja2 macro for rendering a YAML configuration
block with comments and quoted values using Ninjecto's built-in filters:

.. code-block:: jinja

   {# my_library/macros/config_macros.j2 #}
   {% macro config_block(name, value, comment=None) -%}
   {{ comment | comment('yaml') if comment }}
   {{ name }}: {{ value | quote('"') }}
   {%- endmacro %}

Usage in a template:

.. code-block:: jinja

   {% import "my_library/macros/config_macros.j2" as cfgmacros %}

   {{ cfgmacros.config_block('app_name', values.app_name, 'Application name') }}
   {{ cfgmacros.config_block('version', values.version) }}

Or using the ``from`` directive:

.. code-block:: jinja

   {% from 'my_library/macros/config_macros.tpl' import config_block %}

   {{ config_block('app_name', values.app_name, 'Application name') }}
   {{ config_block('version', values.version) }}

Template Inheritance
--------------------

Template inheritance allows you to define a base template with common structure
and extend it in child templates, overriding specific blocks as needed. This
promotes code reuse and consistent layouts across multiple templates.

For more information, see the Jinja2 documentation:

https://jinja.palletsprojects.com/en/stable/templates/#template-inheritance

As an example, lets say you need to render a static website with multiple pages
that share the same header and footer. You can define a base template:

.. code-block:: jinja

   {# my_library/base/base.html.tpl #}
   <!DOCTYPE html>
   <html lang="en">
   <head>
      {% block head %}
      <link rel="stylesheet" href="style.css" />
      <title>{% block title %}{% endblock %} - {{ values.project.name }}</title>
      {% endblock %}
   </head>
   <body>
      <div id="content">{% block content %}{% endblock %}</div>
      <div id="footer">
         {% block footer %}
         &copy; Copyright 2008 {{ values.project.author }}.
         {% endblock %}
      </div>
   </body>
   </html>

Then, in your individual page templates, you can extend this base template
and override the blocks as needed:

.. code-block:: jinja

   {# templates/index.html.tpl #}
   {% extends "my_library/base/base.html.tpl" %}


   {% block title %}Home{% endblock %}
   {% block content %}
   <h1>Welcome to {{ values.project.name }}</h1>
   <p>This is the home page.</p>
   {% endblock %}

When you render ``index.html.tpl``, it will include the common header and
footer from the base template, while customizing the title and content for
the home page.

Configuration
=============

Hierarchical Configuration System
---------------------------------

Ninjecto loads configuration from multiple sources in a specific order, and in
many formats (TOML, YAML, JSON), allowing for flexible environment-specific
setups.

See ``lib/ninjecto/data/config.yaml`` for all available options.

.. code-block:: yaml

   # .ninjerc.yaml
   ninjecto:

     input:
       encoding: "utf-8"

     output:
       encoding: "utf-8"

     filesystemloader:
       encoding: "utf-8"
       followlinks: false

     prefixloader:
       delimiter: "/"

     autoescape:
       enabled_extensions: ["html", "htm", "xml"]
       disabled_extensions: []
       default_for_string: true
       default: false

     undefined:
       clss: 'StrictUndefined'  # Fail on undefined variables

     namespace:
       env:
         safe: true  # Filter envvars considered "unsafe" to be represented as a Python variable.
       git:
         submodules: false  # Cache git info per repository

Template Environment
--------------------

Customize the Jinja2 environment:

.. code-block:: yaml

   ninjecto:
     environment:
       block_start_string: "{%"
       block_end_string: "%}"
       variable_start_string: "{{"
       variable_end_string: "}}"
       comment_start_string: "{#"
       comment_end_string: "#}"
       trim_blocks: true
       lstrip_blocks: true

Please refer to the Jinja2 documentation for more details on these options:
https://jinja.palletsprojects.com/en/latest/api/#jinja2.Environment

And the Ninjecto implementation in ``lib/ninjecto/core.py``:

https://github.com/kuralabs/ninjecto/blob/master/lib/ninjecto/core.py#L261

HashiCorp Vault
---------------

To enable the HashiCorp Vault namespace to retrieve secrets in your templates,
you need to install Ninjecto with the ``vault`` extra:

.. code-block:: bash

   pip install ninjecto[vault]

Then, configure the Vault connection in your configuration file:

.. code-block:: yaml

   ninjecto:
     namespace:
       vault:
         configurations:
           myvault:
             url: "https://myvault.domain.com/"
             token_env: "NINJECTO_MYVAULT_TOKEN"

Or using TOML:

.. code-block:: toml

   [ninjecto.namespace.vault.configurations.myvault]
   url = "https://myvault.domain.com/"
   token_env = "NINJECTO_MYVAULT_TOKEN"

This configuration layout allows to define multiple Vault configurations,
each with its own URL and token environment variable. Set the environment
variable with the Vault token before running Ninjecto:

.. code-block:: bash

   NINJECTO_MYVAULT_TOKEN="s.xxxxxxx" ninjecto -u values.yaml templates/ output/

You can then use the Vault namespace in your templates to fetch secrets:

.. code-block:: jinja

   {{ vault.myvault.mypath.mysecret.mykey }}

Please note that the current implementation supports only the Key/Value secrets
engine version 2 (kv_v2). Patchs to support other engines are welcome.

If you need to access parts of the path or secret names that are not valid
Python variable names (for example, they contain dashes or start with a
number), you can use the bracket notation:

.. code-block:: jinja

   {{ vault['myvault']['mypath']['mysecret']['my-key'] }}

This also applies for dynamic access using input values:

.. code-block:: jinja

   {{ vault[values.vault_name][values.path][values.secret][values.key] }}


CLI Reference
=============

Basic Syntax
------------

.. code-block:: bash

   ninjecto [OPTIONS] SOURCE DESTINATION

Core Options
------------

**Input/Output:**

- ``-o, --output``: Write to specific output file/directory
- ``-i, --output-in``: Write files inside output directory
- ``-f, --force``: Override existing files
- ``-d, --dry-run``: Preview without writing files

**Values:**

- ``-a, --values KEY1=VALUE1 KEY2=VALUE2``: Inline key-value pairs.
  Multiple allowed.

  KEY supports dot notation for nested values, for example:
  ``-a database.host=localhost -a database.port=5432``

  VALUE support strings, integers, float, booleans and ISO 8601 datetimes.
  See ``ninjecto.utils.types.autocast`` for more details.
- ``-u, --values-file FILE``: Load values from file. Supports yaml/json/toml.
  Multiple files allowed; data is merged from left to right, with later files
  overriding earlier ones.
- ``-s, --values-in FORMAT``: Read values from stdin (yaml/json/toml)

**Configuration:**

- ``-c, --config FILE``: Additional configuration files
- ``-l, --library DIR``: Template library directories

**Control:**

- ``-r, --levels N``: Limit directory recursion depth
- ``-p, --parents``: Create parent directories
- ``-v, --verbose``: Increase verbosity

Examples
--------

.. code-block:: bash

   # Basic file processing
   ninjecto template.j2 output.txt

   # With values from multiple sources
   ninjecto -a env=prod -u config.yaml template.j2 output.txt

   # Process directory with custom config
   ninjecto -c config.yaml templates/ output/

   # Dry run with verbose output
   ninjecto -d -vv -u values.yaml src/ dst/

   # Read values from stdin
   echo '{"name": "test"}' | ninjecto --values-in json template.j2 output.txt


Changelog
=========

1.1.0 (2025-11-17)
------------------

Change
~~~~~~

- Removes setup.py in favor of pyproject.toml.


1.0.0 (2025-11-17)
------------------

Change
~~~~~~

- Removes deprecated pkg_resources package.
- Updates build system to use uv.


0.8.0 (2023-06-06)
------------------

New
~~~

- Adds --values-in=[toml,yaml,json] to parse the standard input and allow to
  pass values as a pipe.


0.7.0 (2022-03-24)
------------------

Changes
~~~~~~~

- New version compatible with Jinja2 3.1.0.


0.6.1 (2022-03-24)
------------------

Changes
~~~~~~~

- New version pinning Jinja2 to an older version to avoid breakage caused by
  API changes. Use this version if you need to use Jinja2 < 3.1.0.


0.6.0 (2021-11-22)
------------------

New
~~~

- New namespace "vault" that allows to fetch secrets from a HashiCorp's Vault
  instance.


0.5.0 (2021-07-21)
------------------

Fix
~~~

- Fixes namespaces. "env" and "git" namespaces are now available.


0.4.0 (2020-10-06)
------------------

Fix
~~~

- Fix core on Python 3.8.


0.3.0 (2020-06-10)
------------------

New
~~~

- Allows to define the behavior when encountering undefined values in the
  template.
- Allows conditional creation of files, so depending of a value a file can be
  created or not.
- Rendering is now faster when rendering empty files.
- Ninjecto's CLI now supports passing ``--parents`` to create any parent
  directory of the output directory.
- New filters: ``comment``, ``quote`` and ``read``.
- New filters from awesome Inflection_ package.

  Inflection is now a third party dependency, which includes the new filters:
  ``camelize``, ``dasherize``, ``humanize``, ``ordinal``, ``ordinalize``,
  ``parameterize``, ``pluralize``, ``singularize``, ``tableize``, ``titleize``,
  ``transliterate`` and ``underscore``.

  Also, the Cerberus dependency was dropped as it is unused (for now).

.. _Inflection: https://inflection.readthedocs.io/en/latest/


Fix
~~~

- Values and namespaces are now available globally, in particular inside macros
  in libraries.


0.2.1 (2020-02-04)
------------------

Fix
~~~

- Default output mode will now be set before checking the input and output
  paths, offering a better error message.


0.2.0 (2020-02-03)
------------------

Fix
~~~

- Rendered files will now have the same permissions as the source files.


0.1.1 (2020-02-03)
------------------

Fix
~~~

- Fixes TypeError caused by invalid value of the levels parameter.


0.1.0 (2020-02-01)
------------------

New
~~~

- Development preview.


License
=======

::

   Copyright (C) 2017-2025 KuraLabs S.R.L

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing,
   software distributed under the License is distributed on an
   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
   KIND, either express or implied.  See the License for the
   specific language governing permissions and limitations
   under the License.
