.. _user_guide:

:octicon:`person` User Guide
============================

.. toctree::
    :maxdepth: 2
    :hidden:

    getting_started
    configuration/index
    examples/index
    features/index

Welcome to SQLAlchemy-Exasol
-----------------------------

SQLAlchemy-Exasol is a dialect extension for SQLAlchemy, implementing support for Exasol databases.
The provided dialect is based on `PyExasol <https://github.com/exasol/pyexasol/>`__, which relies
on the `Websocket-client API <https://github.com/exasol/websocket-api>`__.

.. note::
    For more details on SQLAlchemy, please consult its `general documentation <https://docs.sqlalchemy.org/en/20/>`_
    and `dialect-specific documentation <https://docs.sqlalchemy.org/en/20/dialects/>`__.

Getting Started
---------------
For pre-requisites, installing `sqlalchemy-exasol`, and creating your first connection,
please see our :ref:`getting_started` guide.


Diving Deeper
-------------

* For information on parameters for your connection, see :ref:`configuration`.
* For details on what features are available, see :ref:`features`.
* Coded examples are provided in :ref:`examples`.
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
    - Insert multiple empty rows via prepared statements does not work in all cases.
    - The Exasol dialect does not support returning for multiple inserts.
