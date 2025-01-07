SQLAlchemy-Exasol
=================
SQLAlchemy-Exasol is an SQLAlchemy dialect extension.

Overview
--------
The dialect is the system SQLAlchemy uses to communicate with various types of DBAPI implementations and databases.
The sections that follow contain reference documentation and notes specific to the usage of each backend,
as well as notes for the various DBAPIs.

For more details have a look into the `SQLAlchemy documentation <https://docs.sqlalchemy.org/en/13/dialects/>`_.

Getting Started
---------------

#. `Install the Exasol-ODBC driver <https://docs.exasol.com/db/latest/connect_exasol/drivers/odbc.htm>`_

#. Add `sqlalchemy-exasol <https://pypi.org/project/sqlalchemy-exasol/>`_ as a dependency

    .. code-block:: shell

        $ pip install sqlalchemy-exasol

#. Execute queries

    .. code-block:: python

        from sqlalchemy import create_engine
        url = "exa+pyodbc://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?CONNECTIONLCALL=en_US.UTF-8&driver=EXAODBC"
        e = create_engine(url)
        r = e.execute("select 42 from dual").fetchall()


For more details on SQLAlchemy consult it's `documenation <https://docs.sqlalchemy.org/en/13/>`_.

.. toctree::
   :maxdepth: 3
   :hidden:

   readme
   changelog
   developer_guide/index
