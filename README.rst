SQLAlchemy Dialect for EXASOL DB
================================


.. image:: https://github.com/exasol/sqlalchemy_exasol/workflows/CI/badge.svg?branch=master
    :target: https://github.com/exasol/sqlalchemy_exasol/actions?query=workflow%3ACI
     :alt: CI Status

.. image:: https://img.shields.io/pypi/v/sqlalchemy_exasol
     :target: https://pypi.org/project/sqlalchemy-exasol/
     :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/sqlalchemy-exasol
    :target: https://pypi.org/project/sqlalchemy-exasol
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/badge/exasol-7.1.9%20%7C%207.0.18-green
    :target: https://www.exasol.com/
    :alt: Exasol - Supported Version(s)

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Formatter - Black

.. image:: https://img.shields.io/badge/imports-isort-ef8336.svg
    :target: https://pycqa.github.io/isort/
    :alt: Formatter - Isort

.. image:: https://img.shields.io/badge/pylint-6.4-yellowgreen
    :target: https://github.com/PyCQA/pylint
    :alt: Pylint

.. image:: https://img.shields.io/pypi/l/sqlalchemy-exasol
     :target: https://opensource.org/licenses/BSD-2-Clause
     :alt: License

.. image:: https://img.shields.io/github/last-commit/exasol/sqlalchemy-exasol
     :target: https://pypi.org/project/sqlalchemy-exasol/
     :alt: Last Commit

.. image:: https://img.shields.io/pypi/dm/sqlalchemy-exasol
    :target: https://pypi.org/project/sqlalchemy-exasol
    :alt: PyPI - Downloads


How to get started
------------------

We assume you have a good understanding of (unix)ODBC. If not, make sure you
read their documentation carefully - there are lot's of traps 🪤 to step into.

Turbodbc support
````````````````

.. warning::

    Maintenance of this feature is on hold. Also it is very likely that turbodbc support will be dropped in future versions.

- You can use Turbodbc with sqlalchemy_exasol if you use a python version >= 3.8.
- Multi row update is not supported, see
  `test/test_update.py <test/test_update.py>`_ for an example



Meet the system requirements
````````````````````````````

On Linux/Unix like systems you need:

- Python
- An Exasol DB (e.g. `docker-db <test_docker_image_>`_ or a `cloud instance <test_drive_>`_)
- The packages unixODBC and unixODBC-dev >= 2.2.14
- The Exasol `ODBC driver <odbc_driver_>`_
- The ODBC.ini and ODBCINST.ini configurations files setup

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

Notes
+++++

- Schema name and parameters are optional for the host url
- At least on Linux/Unix systems it has proven valuable to pass 'CONNECTIONLCALL=en_US.UTF-8' as a url parameter. This will make sure that the client process (Python) and the EXASOL driver (UTF-8 internal) know how to interpret code pages correctly.
- Always use all lower-case identifiers for schema, table and column names. SQLAlchemy treats all lower-case identifiers as case-insensitive, the dialect takes care of transforming the identifier into a case-insensitive representation of the specific database (in case of EXASol this is upper-case as for Oracle)
- As of Exasol client driver version 4.1.2 you can pass the flag 'INTTYPESINRESULTSIFPOSSIBLE=y' in the connection string (or configure it in your DSN). This will convert DECIMAL data types to Integer-like data types. Creating integers is a factor three faster in Python than creating Decimals.

.. _developer guide: https://github.com/exasol/sqlalchemy-exasol/blob/master/doc/developer_guide/developer_guide.rst
.. _odbc_driver: https://docs.exasol.com/db/latest/connect_exasol/drivers/odbc/odbc_linux.htm
.. _test_drive: https://www.exasol.com/test-it-now/cloud/
.. _test_docker_image: https://github.com/exasol/docker-db

Development & Testing
`````````````````````
See `developer guide`_

Websocket support
-----------------

.. attention::

    The Websocket support is currently in Beta, therefore it should not be used in production.
    We also recommend to have a look into the known issues, before you start using it.

    If you encounter any issue, please `create an issue <https://github.com/exasol/sqlalchemy-exasol/issues/new?assignees=&labels=bug&projects=&template=bug.md&title=%F0%9F%90%9E+%3CInsert+Title%3E>`_.
    With your feedback, we will be able to stabilize this feature more quickly.

What is Websocket support?
``````````````````````````
In the context of SQLA and Exasol, Websocket support means that an SQLA dialect
supporting the `Exasol Websocket Protocol <https://github.com/exasol/websocket-api>`_
is provided.

Using the websocket based protocol instead over ODBC will provide various advantages:

* Less System Dependencies
* Easier to use than ODBC based driver(s)
* Lock free metadata calls etc.

For further details `Why a Websockets API  <https://github.com/exasol/websocket-api#why-a-websockets-api>`_.

Examples Usage(s)
`````````````````

.. code-block:: python

    from sqla import create_engine

    engine = create_engine("exa+websocket://sys:exasol@127.0.0.1:8888")
    with engine.connect() as con:
        ...

.. code-block:: python

    from sqla import create_engine

    # ATTENTION:
    # In terms of security it is NEVER a good idea to turn of certificate validation!!
    # In rare cases it may be handy for non-security related reasons.
    # That said, if you are not a 100% sure about your scenario, stick with the
    # secure defaults.
    # In most cases, having a valid certificate and/or configuring the truststore(s)
    # appropriately is the best/correct solution.
    engine = create_engine("exa+websocket://sys:exasol@127.0.0.1:8888?SSLCertificate=SSL_VERIFY_NONE")
    with engine.connect() as con:
        ...

Supported Connection Parameters
```````````````````````````````
.. list-table::

   * - Parameter
     - Values
     - Comment
   * - ENCRYPTION
     - Y, Yes, N, No
     - Y or Yes Enable Encryption (TLS) default, N or No disable Encryption
   * - SSLCertificate
     - SSL_VERIFY_NONE
     - Disable certificate validation


Known Issues
````````````

* Literal casts within prepared statements do not work
    - :code:`INSERT INTO t (x) VALUES (CAST(? AS VARCHAR(50)));`
* Various conversions regarding float, decimals
    - Certain scenarios still yield a :code:`string` type instead :code:`float` or :code:`decimal` type.
* Insert
    - Insert multiple rows via prepared statements does not work in all cases
    - Insert from SELECT does not work
* For some prepared statements, the wss protocol type conversion does not work properly
    - Error messages usually state some JSON type mismatch, e.g.: '... getString: JSON value is not a string ...'
* Known failing tests of the SQLA compliance test suite
    - FAILED test/integration/sqlalchemy/test_suite.py::CastTypeDecoratorTest_exasol+exasol_driver_websocket_dbapi2::test_special_type - sqlalchemy.exc.DBAPIError: (exasol.driver.websocket._errors.Error)
    - FAILED test/integration/sqlalchemy/test_suite.py::ExistsTest_exasol+exasol_driver_websocket_dbapi2::test_select_exists - sqlalchemy.exc.DBAPIError: (exasol.driver.websocket._errors.Error)
    - FAILED test/integration/sqlalchemy/test_suite.py::ExistsTest_exasol+exasol_driver_websocket_dbapi2::test_select_exists_false - sqlalchemy.exc.DBAPIError: (exasol.driver.websocket._errors.Error)
    - FAILED test/integration/sqlalchemy/test_suite.py::InsertBehaviorTest_exasol+exasol_driver_websocket_dbapi2::test_empty_insert_multiple - sqlalchemy.exc.DBAPIError: (exasol.driver.websocket._errors.Error)
    - ERROR  test/integration/sqlalchemy/test_suite.py::InsertBehaviorTest_exasol+exasol_driver_websocket_dbapi2::test_empty_insert_multiple_teardown - ERROR
    - FAILED test/integration/sqlalchemy/test_suite.py::InsertBehaviorTest_exasol+exasol_driver_websocket_dbapi2::test_insert_from_select - sqlalchemy.exc.DBAPIError: (exasol.driver.websocket._errors.Error)
    - FAILED test/integration/sqlalchemy/test_suite.py::InsertBehaviorTest_exasol+exasol_driver_websocket_dbapi2::test_insert_from_select_with_defaults - sqlalchemy.exc.DBAPIError: (exasol.driver.websocket._errors.Error)
    - FAILED test/integration/sqlalchemy/test_suite.py::NumericTest_exasol+exasol_driver_websocket_dbapi2::test_float_as_decimal - sqlalchemy.exc.DBAPIError: (exasol.driver.websocket._errors.Error)
    - FAILED test/integration/sqlalchemy/test_suite.py::NumericTest_exasol+exasol_driver_websocket_dbapi2::test_float_as_float - sqlalchemy.exc.DBAPIError: (exasol.driver.websocket._errors.Error)
    - FAILED test/integration/sqlalchemy/test_suite.py::NumericTest_exasol+exasol_driver_websocket_dbapi2::test_float_coerce_round_trip - AssertionError: '15.7563' != 15.7563
    - FAILED test/integration/sqlalchemy/test_suite.py::NumericTest_exasol+exasol_driver_websocket_dbapi2::test_float_custom_scale - sqlalchemy.exc.DBAPIError: (exasol.driver.websocket._errors.Error)
    - FAILED test/integration/sqlalchemy/test_suite.py::NumericTest_exasol+exasol_driver_websocket_dbapi2::test_numeric_as_float - AssertionError: {'15.7563'} != {15.7563}
    - FAILED test/integration/sqlalchemy/test_suite.py::NumericTest_exasol+exasol_driver_websocket_dbapi2::test_render_literal_numeric_asfloat - AssertionError: assert '15.7563' in [15.7563]
