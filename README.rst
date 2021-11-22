===============================
Ninjecto - Ninja Injection Tool
===============================

Template rendering and variable injection made easy.

.. image:: https://circleci.com/gh/kuralabs/ninjecto.svg?style=shield
   :target: https://circleci.com/gh/kuralabs/ninjecto
   :alt: Build Status

.. image:: https://img.shields.io/pypi/v/ninjecto
   :target: https://pypi.org/project/ninjecto/
   :alt: PyPI

.. image:: https://img.shields.io/github/license/kuralabs/ninjecto
   :target: https://choosealicense.com/licenses/apache-2.0/
   :alt: License


Documentation
=============

    https://docs.kuralabs.io/ninjecto/


Install
=======

.. code-block:: sh

    pip3 install ninjecto


Changelog
=========

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

  - Values and namespaces are now available globally, in particular inside macros in libraries.


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

   Copyright (C) 2017-2021 KuraLabs S.R.L

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
