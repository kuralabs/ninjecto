.. toctree::

===============
Developer Guide
===============


Setup Development Environment
=============================

#. Install ``pip3`` and development dependencies:

   .. code-block:: sh

      wget https://bootstrap.pypa.io/get-pip.py
      sudo python3 get-pip.py
      sudo pip3 install tox

#. Install a native toolchain to build extensions and other required tools:

   .. code-block:: sh

      sudo apt install python3-dev build-essential graphviz

#. Optionally, it is recommended to install the ``webdev`` package to run a
   development web server from a local directory:

   .. code-block:: sh

      sudo pip3 install webdev
      webdev .tox/doc/tmp/html


Building Package
================

.. code-block:: sh

   tox -e build

Output will be available at ``dist/``.

- Source distribution: ``ninjecto-<version>.tar.gz``.
- Python wheel: ``ninjecto-<version>-py3-none-any.whl``
- Binary wheel: ``ninjecto-<version>-cp36-cp36m-linux_x86_64.whl``

.. note::

   The tags of the binary wheel will change depending on the interpreter and
   operating system you build the binary wheel on.


Building Documentation
======================

.. code-block:: sh

   tox -e doc

Output will be available at ``.tox/doc/tmp/html``.

.. code-block:: sh

   webdev .tox/doc/tmp/html


Running Test Suite
==================

.. code-block:: sh

   tox -e test

Output will be available at ``.tox/test/tmp/``.

.. code-block:: sh

   webdev .tox/test/tmp/

- Test results: ``tests.xml``.
- Coverage results: ``coverage.xml``.
- Coverage report: ``coverage.html``.
