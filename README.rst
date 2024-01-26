SQLAlchemy Dialect for EXASOL DB
================================


.. image:: https://github.com/exasol/sqlalchemy-exasol/actions/workflows/ci-cd.yml/badge.svg?branch=master&event=push
    :target: https://github.com/exasol/sqlalchemy-exasol/actions/workflows/ci-cd.yml
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


Getting Started with SQLAlchemy-Exasol
--------------------------------------
SQLAlchemy-Exasol supports multiple dialects, primarily differentiated by whether they are ODBC or Websocket based.

Choosing a Dialect
++++++++++++++++++

We recommend using the Websocket-based dialect due to its simplicity. ODBC-based dialects demand a thorough understanding of (Unix)ODBC, and the setup is considerably more complex.

.. warning::

    The maintenance of Turbodbc support is currently paused, and it may be phased out in future versions.
    We are also planning to phase out the pyodbc support in the future.



System Requirements
-------------------
- Python
- An Exasol DB (e.g. `docker-db <test_docker_image_>`_ or a `cloud instance <test_drive_>`_)

.. note::

   For ODBC-Based Dialects, additional libraries required for ODBC are necessary
   (for further details, checkout the `developer guide`_).

Setting Up Your Python Project
------------------------------

Install SQLAlchemy-Exasol:

.. code-block:: shell

    $ pip install sqlalchemy-exasol

.. note::

   To use an ODBC-based dialect, you must specify it as an extra during installation.

   .. code-block:: shell

      pip install "sqlalchemy-exasol[pydobc]"
      pip install "sqlalchemy-exasol[turbodbc]"


Using SQLAlchemy with EXASOL DB
-------------------------------

**Websocket based Dialect:**

.. code-block:: python

	from sqlalchemy import create_engine
	url = "exa+websocket://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?CONNECTIONLCALL=en_US.UTF-8"
	e = create_engine(url)
	r = e.execute("select 42 from dual").fetchall()

Examples:

.. code-block:: python

    from sqlalchemy import create_engine

    engine = create_engine("exa+websocket://sys:exasol@127.0.0.1:8888")
    with engine.connect() as con:
        ...

.. code-block:: python

    from sqlalchemy import create_engine

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


**Pyodbc (ODBC based Dialect):**

.. code-block:: python

	from sqlalchemy import create_engine
	url = "exa+pyodbc://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?CONNECTIONLCALL=en_US.UTF-8&driver=EXAODBC"
	e = create_engine(url)
	r = e.execute("select 42 from dual").fetchall()

**Turbodbc (ODBC based Dialect):**

.. code-block:: python

	from sqlalchemy import create_engine
	url = "exa+turbodbc://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?CONNECTIONLCALL=en_US.UTF-8&driver=EXAODBC"
	e = create_engine(url)
	r = e.execute("select 42 from dual").fetchall()


Features
--------

- SELECT, INSERT, UPDATE, DELETE statements

General Notes
-------------

- Schema name and parameters are optional for the host url
- At least on Linux/Unix systems it has proven valuable to pass 'CONNECTIONLCALL=en_US.UTF-8' as a url parameter. This will make sure that the client process (Python) and the EXASOL driver (UTF-8 internal) know how to interpret code pages correctly.
- Always use all lower-case identifiers for schema, table and column names. SQLAlchemy treats all lower-case identifiers as case-insensitive, the dialect takes care of transforming the identifier into a case-insensitive representation of the specific database (in case of EXASol this is upper-case as for Oracle)
- As of Exasol client driver version 4.1.2 you can pass the flag 'INTTYPESINRESULTSIFPOSSIBLE=y' in the connection string (or configure it in your DSN). This will convert DECIMAL data types to Integer-like data types. Creating integers is a factor three faster in Python than creating Decimals.

.. _developer guide: https://github.com/exasol/sqlalchemy-exasol/blob/master/doc/developer_guide/developer_guide.rst
.. _odbc_driver: https://docs.exasol.com/db/latest/connect_exasol/drivers/odbc/odbc_linux.htm
.. _test_drive: https://www.exasol.com/test-it-now/cloud/
.. _test_docker_image: https://github.com/exasol/docker-db

Known Issues
------------
* Insert
    - Insert multiple empty rows via prepared statements does not work in all cases

Development & Testing
---------------------
See `developer guide`_


