.. _getting_started:

Getting Started
===============

Prerequisites
-------------

- Exasol >= 7.1
- Python >= 3.10

Installing
----------

`sqlalchemy-exasol is distributed through PyPI <https://pypi.org/project/sqlalchemy_exasol/>`__. It can be installed via pip, poetry, or any other compatible dependency management tool:

.. code-block:: bash

   pip install sqlalchemy-exasol

.. note::

    SQLAlchemy will be installed as well, as it is a required dependency for SQLAlchemy-Exasol.

First Steps
-----------

For a user's first step, we recommend, running some basic queries on a safe-to-test table.
`sqlalchemy-exasol` provides examples for this purpose, demonstrating the most important features.
The examples use the :ref:`instance_url` available since SQLAlchemy 1.4.
It is still possible to use a :ref:`url_string` instead.

Connection Configuration
++++++++++++++++++++++++
For running the examples, file ``examples/config.py`` provides a default connection configuration
for an Exasol Docker DB. If your setup differs, you can override the default values by setting
exported environment variables, as specified in the docstring.

.. collapse:: config.py
    :open:

    .. literalinclude:: ../../examples/config.py
           :language: python3

Testing your Connection
+++++++++++++++++++++++
To test that your connection works and to execute your first query, please
run ``examples/getting_started/1_create_and_test_connection.py``.

.. collapse:: 1_create_and_test_connection.py
    :open:

    .. literalinclude:: ../../examples/getting_started/1_create_and_test_connection.py
           :language: python3
