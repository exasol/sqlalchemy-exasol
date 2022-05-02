SQLAlchemy Dialect for EXASOL DB
================================


.. image:: https://github.com/exasol/sqlalchemy_exasol/workflows/CI-CD/badge.svg?branch=master
    :target: https://github.com/exasol/sqlalchemy_exasol/actions?query=workflow%3ACI-CD
.. image:: https://img.shields.io/pypi/v/sqlalchemy_exasol
     :target: https://pypi.org/project/sqlalchemy-exasol/
     :alt: PyPI Version
.. image:: https://img.shields.io/conda/vn/conda-forge/sqlalchemy_exasol.svg
     :target: https://anaconda.org/conda-forge/sqlalchemy_exasol
     :alt: Conda Version

This is an SQLAlchemy dialect for the EXASOL database.

- EXASOL: http://www.exasol.com
- SQLAlchemy: http://www.sqlalchemy.org

How to get started
------------------

We assume you have a good understanding of (unix)ODBC. If not, make sure you
read their documentation carefully - there are lot's of traps 🪤 to step into.

Meet the system requirements
````````````````````````````

On Linux/Unix like systems you need:

- An Exasol DB (e.g. `docker-db <test_docker_image_>`_ or a `cloud instance <test_drive_>`_)

  - >= 7.1.6
  - >= 7.0.16

- The packages unixODBC and unixODBC-dev >= 2.2.14
- Python >= 3.7
- The Exasol `ODBC driver <odbc_driver_>`_
- The ODBC.ini and ODBCINST.ini configurations files setup

Turbodbc support
````````````````

- You can use Turbodbc with sqlalchemy_exasol if you use a python version >= 3.7.
- Multi row update is not supported, see
  `test/test_update.py <test/test_update.py>`_ for an example


Setup your python project and install sqlalchemy-exasol
```````````````````````````````````````````````````````

.. code-block:: shell

    $ pip install sqlalchemy-exasol

for turbodbc support:

.. code-block:: shell

    $ pip install sqlalchemy-exasol[turbodbc]

Talk to the EXASOL DB using SQLAlchemy
``````````````````````````````````````

.. code-block:: python

	from sqlalchemy import create_engine
	url = "exa+pyodbc://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?CONNECTIONLCALL=en_US.UTF-8&driver=EXAODBC"
	e = create_engine(url)
	r = e.execute("select 42 from dual").fetchall()

to use turbodbc as driver:

.. code-block:: python

	from sqlalchemy import create_engine
	url = "exa+turbodbc://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?CONNECTIONLCALL=en_US.UTF-8&driver=EXAODBC"
	e = create_engine(url)
	r = e.execute("select 42 from dual").fetchall()


The dialect supports two types of connection urls creating an engine. A DSN (Data Source Name) mode and a host mode:

.. list-table::

   * - Type
     - Example
   * - DSN URL
     - 'exa+pyodbc://USER:PWD@exa_test'
   * - HOST URL
     - 'exa+pyodbc://USER:PWD@192.168.14.227..228:1234/my_schema?parameter'

Features
++++++++

- SELECT, INSERT, UPDATE, DELETE statements
- you can even use the MERGE statement (see unit tests for examples)

Notes
+++++

- Schema name and parameters are optional for the host url
- At least on Linux/Unix systems it has proven valuable to pass 'CONNECTIONLCALL=en_US.UTF-8' as a url parameter. This will make sure that the client process (Python) and the EXASOL driver (UTF-8 internal) know how to interpret code pages correctly.
- Always use all lower-case identifiers for schema, table and column names. SQLAlchemy treats all lower-case identifiers as case-insensitive, the dialect takes care of transforming the identifier into a case-insensitive representation of the specific database (in case of EXASol this is upper-case as for Oracle)
- As of Exasol client driver version 4.1.2 you can pass the flag 'INTTYPESINRESULTSIFPOSSIBLE=y' in the connection string (or configure it in your DSN). This will convert DECIMAL data types to Integer-like data types. Creating integers is a factor three faster in Python than creating Decimals.

Development & Testing
`````````````````````
See `developer guide`_

.. _developer guide: https://github.com/exasol/sqlalchemy-exasol/blob/master/doc/developer_guide/developer_guide.rst
.. _odbc_driver: https://docs.exasol.com/db/latest/connect_exasol/drivers/odbc/odbc_linux.htm
.. _test_drive: https://www.exasol.com/test-it-now/cloud/
.. _test_docker_image: https://github.com/exasol/docker-db
