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
    beforehand in another database-manipulation tool to ensure that the output you will
    receive is as desired (and not, i.e. millions of rows).

    The example use the :ref:`instance_url` available since SQLAlchemy 1.4. It is still
    possible to use a :ref:`url_string` instead.


.. code-block:: python

    from sqlalchemy import create_engine, text, URL

    url_object = URL.create(
        drivername="exa+websocket",
        username="sys",
        password="exasol",
        host="127.0.0.1",
        port="8563",
    )

    engine = create_engine(url_object)
    # All literal text should be passed through `text()` before execution
    sql_text = text("SELECT 42 FROM DUAL")
    with engine.connect() as con:
        result = con.execute(sql_text).fetchall()

Diving Deeper
-------------

* For information on setup options, see :ref:`configuration`.
* With SQLAlchemy 2.x, there are more options regarding sessions and how commits
  behave within those, it is recommended to check out the
  `Session Transaction <https://docs.sqlalchemy.org/en/20/orm/session_transaction.html>`__ page
  and adapt your code according to the best practices.
