SQLAlchemy-Exasol
=================
SQLAlchemy-Exasol is a dialect extension for SQLAlchemy, implementing support for Exasol databases.

Getting Started
---------------

#. Install the `SQLAlchemy-Exasol extension <https://pypi.org/project/sqlalchemy-exasol/>`_

    .. code-block:: shell

        $ pip install sqlalchemy-exasol

    .. note::

        SQLAlchemy will be installed due to the fact that it is an required dependency for SQLAlchemy-Exasol.

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
   developer_guide/index
   changelog
