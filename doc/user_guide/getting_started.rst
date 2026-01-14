.. _getting_started:

Getting Started
===============

This guide is designed to get a new user started with ``sqlalchemy-exasol``.

Prerequisites
-------------

- Exasol >= 7.1
- Python >= 3.10

Installing
----------

`sqlalchemy-exasol is distributed through PyPI <https://pypi.org/project/sqlalchemy_exasol/>`__.
It can be installed via pip, poetry, or any other compatible dependency management tool:

.. code-block:: bash

   pip install sqlalchemy-exasol

.. note::

    SQLAlchemy will be installed as well, as it is a required dependency for SQLAlchemy-Exasol.

First Steps
-----------

For a user's first step, we recommend, running some basic queries on a safe-to-test table.
As a first step, we recommend executing:

.. literalinclude:: ../../examples/getting_started/0_create_and_test_connection.py
       :language: python3
       :caption: examples/getting_started/0_create_and_test_connection.py

Next Steps
----------

The SQLAlchemy-Exasol documentation covers many topics at different levels of experience:

* For best securing your connection, see :ref:`security`.
* For other connection parameters, see :ref:`engine_configuration`.
* Check out the available :ref:`features` & related :ref:`examples` for this purpose, demonstrating the most
  important features.
