.. _examples:

Examples
========

Here we group and present the code for our examples. While there are docstrings and
comments in the code to provide context, please look to our :ref:`getting_started`
guide, pages in :ref:`features`, and the
`general documentation of SQLAlchemy <https://docs.sqlalchemy.org/en/20/>`_
for a more detailed walkthrough.

Preparation
-----------

Some basic preparation steps are required to see the examples in action:

#. Download the `SQLAlchemy-Exasol source code <https://github.com/exasol/sqlalchemy-exasol/>`__.\
#. Inside the folder where you have SQLAlchemy-Exasol's source code, install the dependencies using:

    .. code-block:: bash

        poetry install

#. Make sure you have installed or have access to an Exasol database. For **testing** purposes, you may use:
    - `exasol/docker-db <https://hub.docker.com/r/exasol/docker-db/tags>`__, which can be easily accessed by using ``poetry run -- nox -s db:start``
    - the free `Exasol Community Edition <https://www.exasol.com/free-signup-community-edition/>`__

#. Open the ``/examples/`` directory and edit the file configuration file, as described in :ref:`example_configuration`.
#. To verify that your connection configuration is correct, run the code, as described in :ref:`example_connection`:
#. Now, you may run whatever examples you would like:

    .. code-block:: bash

        poetry run -- python examples/<path_to_desired_module>.py

.. _example_configuration:

Connection Configuration
------------------------

For running the examples, file ``examples/config.py`` provides a default connection configuration
for an Exasol Docker DB. If your setup differs, you can either modify the values in the
``CONNECTION_CONFIG`` initialization or override the default values by setting
exported environment variables, as specified in the docstring.

.. literalinclude:: ../../../examples/config.py
       :language: python3
       :caption: examples/config.py

.. _example_connection:

Testing your Connection
-----------------------

To test that your connection works from the ``examples/config.py`` and to execute
your first query, please run :ref:`example_connection`:

.. code-block::

    poetry run -- python examples/getting_started/1_test_config_connection.py


.. literalinclude:: ../../../examples/getting_started/1_test_config_connection.py
       :language: python3
       :caption: examples/getting_started/1_test_config_connection.py
