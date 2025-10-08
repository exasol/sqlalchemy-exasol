.. _user_guide:

:octicon:`person` User Guide
============================

SQLAlchemy-Exasol is a dialect extension for SQLAlchemy, implementing support for Exasol databases.

Getting Started
~~~~~~~~~~~~~~~

#. Install the `SQLAlchemy-Exasol extension <https://pypi.org/project/sqlalchemy_exasol/>`_

    .. code-block:: shell

        $ pip install sqlalchemy-exasol

    .. note::

        SQLAlchemy will be installed due to the fact that it is an required dependency for SQLAlchemy-Exasol.

#. Execute queries

    .. code-block:: python

        from sqlalchemy import create_engine, sql
        url = "exa+pyodbc://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?CONNECTIONLCALL=en_US.UTF-8&driver=EXAODBC"
        e = create_engine(url)
        query = "select 42 from dual"
        with engine.connect() as con:
            result = con.execute(sql.text(query)).fetchall()


For more details on SQLAlchemy consult it's `documentation <https://docs.sqlalchemy.org/en/13/>`_.

Readme
~~~~~~

.. include:: ../README.rst
   :end-before: Development & Testing
