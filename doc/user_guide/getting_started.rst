Getting Started
===============

Welcome to SQLAlchemy-Exasol
-----------------------------

SQLAlchemy-Exasol is a dialect extension for SQLAlchemy, implementing support for Exasol databases.
The provided dialect is based on `PyExasol <https://github.com/exasol/pyexasol/>`__, which relies
on the `Websocket-client API <https://github.com/exasol/websocket-api>`__.

.. note::
    For more details on SQLAlchemy, please consult its `general documentation <https://docs.sqlalchemy.org/en/20/>`_
    and `dialect-specific documentation <https://docs.sqlalchemy.org/en/20/dialects/>`.

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
For this purpose and to demonstrate what a user can do with `sqlalchemy-exasol`,
examples are provided.

.. note::
    These examples are written assuming a newly installed or otherwise safe-to-test
    Exasol database (i.e. Exasol Docker DB). The examples use the :ref:`instance_url`
    available since SQLAlchemy 1.4. It is still possible to use a :ref:`url_string` instead.

Connection Configuration
++++++++++++++++++++++++
For running the examples, a default connection configuration for an Exasol Docker DB has
been provided in the   ``examples/config.py``. If your setup differs, you can override
the default values by setting exported environment variables, as specified in the
docstring.

.. collapse:: config.py
    :open:

    .. literalinclude:: ../../examples/config.py
           :language: python3

Testing your Connection
+++++++++++++++++++++++
To test that your connection works & perform your first query, please
execute ``examples/getting_started/1_create_and_test_connection.py``.

.. collapse:: 1_create_and_test_connection.py
    :open:

    .. literalinclude:: ../../examples/getting_started/1_create_and_test_connection.py
           :language: python3

Diving Deeper
-------------

* For information on setup options, see :ref:`configuration`.
* With SQLAlchemy 2.x, there are more options regarding sessions and how commits
  behave within those, it is recommended to check out the
  `Session Transaction <https://docs.sqlalchemy.org/en/20/orm/session_transaction.html>`__ page
  and adapt your code according to the best practices.

General Tips
------------

* Always use lowercase identifiers for schema, table, and column names. SQLAlchemy
  treats lowercase identifiers as case-insensitive. The dialect takes care of
  transforming the identifier into a case-insensitive representation for the specific
  database. In the case of Exasol, this is uppercase.

Known Issues
------------
* Insert
    - Insert multiple empty rows via prepared statements does not work in all cases
