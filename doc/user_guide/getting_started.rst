Getting Started
===============

Welcome to SQLAlchemy-Exasol
-----------------------------

SQLAlchemy-Exasol is a dialect extension for SQLAlchemy, implementing support for Exasol databases.
The provided dialect is based on `PyExasol <https://github.com/exasol/pyexasol/>`__, which relies
on the `Websocket-client API <https://github.com/exasol/websocket-api>`__.

.. note::
    For more details on SQLAlchemy, please consult its `documentation <https://docs.sqlalchemy.org/en/14/>`_.

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

For a user's first steps, it is recommended to try out running basic queries on a safe-to-test table.

.. note::
    These examples are written assuming a newly installed or otherwise safe-to-test
    Exasol database. If that is not the case, it is recommended to check your query
    beforehand in another DB-manipulation tool to ensure that the output you will
    receive is as desired (and not, i.e. millions of rows).
