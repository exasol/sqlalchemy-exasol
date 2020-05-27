SQLAlchemy Dialect for EXASOL DB
================================


.. image:: https://github.com/blue-yonder/sqlalchemy_exasol/workflows/CI-CD.yml/badge.svg?branch=master
    :target: https://github.com/blue-yonder/sqlalchemy_exasol/actions?query=workflow%3ACI-CD
.. image:: https://requires.io/github/blue-yonder/sqlalchemy_exasol/requirements.svg?branch=master
     :target: https://requires.io/github/blue-yonder/sqlalchemy_exasol/requirements/?branch=master
     :alt: Requirements Status
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
read their documentation carefully - there are lot's of traps to step into.

Get the EXASolution database
````````````````````````````

If you do not have access to an EXASolution database, download EXASolo for free
from EXASOL: http://www.exasol.com/en/test-drive/

The database is a VM image. You will need VirtualBox, VMWare Player, or KVM to
run the database. Start the database and make sure you can connect to it as
described in the How-To from EXASOL.

Meet the system requirements
````````````````````````````

On Linux/Unix like systems you need:

- the packages unixODBC and unixODBC-dev >= 2.2.14
- Python >= 2.7
- Download and install the ODBC client drivers from EXASOL >= 5
- configure ODBC.ini and ODBCINST.ini

Turbodbc support
````````````````

- Turbodbc and sqlalchemy_exasol as well do now support python 2.7, 3.4 and 3.6.
- Multi row update is not supported, see
  `test/test_update.py <test/test_update.py>`_ for an example.


Setup you python project and install sqlalchemy-exasol
``````````````````````````````````````````````````````

::

	> pip install sqlalchemy-exasol

for turbodbc support:

::

	> pip install sqlalchemy-exasol[turbodbc]

Talk to EXASolution using SQLAlchemy
````````````````````````````````````

::

	from sqlalchemy import create_engine
	e = create_engine("exa+pyodbc://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?CONNECTIONLCALL=en_US.UTF-8&driver=EXAODBC")
	r = e.execute("select 42 from dual").fetchall()

to use turbodbc as driver:

::

	from sqlalchemy import create_engine
	e = create_engine("exa+turbodbc://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?CONNECTIONLCALL=en_US.UTF-8&driver=EXAODBC")
	r = e.execute("select 42 from dual").fetchall()


The dialect supports two connection urls for create_engine. A DSN (Data Source Name) mode and a host mode:

========  ====================================================================
DSN url   'exa+pyodbc://USER:PWD@exa_test'
Host url  'exa+pyodbc://USER:PWD@192.168.14.227..228:1234/my_schema?parameter'
========  ====================================================================

*Features*:

- SELECT, INSERT, UPDATE, DELETE statements
- you can even use the MERGE statement (see unit tests for examples)

*Note*:

- Schema name and parameters are optional for the host url string
- At least on Linux/Unix systems it has proven valuable to pass 'CONNECTIONLCALL=en_US.UTF-8' as a url parameter. This will make sure that the client process (Python) and the EXASOL driver (UTF-8 internal) know how to interpret code pages correctly.
- Always use all lower-case identifiers for schema, table and column names. SQLAlchemy treats all lower-case identifiers as case-insensitive, the dialect takes care of transforming the identifier into a case-insensitive representation of the specific database (in case of EXASol this is upper-case as for Oracle)
- As of EXASol client driver version 4.1.2 you can pass the flag 'INTTYPESINRESULTSIFPOSSIBLE=y' in the connection string (or configure it in your DSN). This will convert DECIMAL data types to Integer-like data types. Creating integers is a factor three faster in Python than creating Decimals.


Unit tests
``````````

To run the unit tests you need:

- set the `default` connection string in the `setup.cfg` file, which should contain an existing schema to run tests against.  Note that the tests also use a schema "test_schema";
- set the `DRIVER` path under the `EXAODBC` section in the `odbcconfig/odbcinst.ini` file;
- set the `ODBCINSTINI` and `ODBCINST` environment variables to point to the full path of `odbcconfig/odbcinst.ini`

and finally run the unit tests:

    $ py.test test/


Troubleshooting
```````````````

The unixodbc Stack is not the most friendly for programmers. If you get strange errors from the driver mangager, you might have an issue with the names of the unixodbc libs. Have a look at https://github.com/blue-yonder/sqlalchemy_exasol/blob/master/fix_unixodbc_so.sh to find ideas on how to fix this on Ubuntu. Good luck!

