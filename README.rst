SQLAlchemy Dialect for EXASOL DB
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. image:: https://github.com/exasol/sqlalchemy-exasol/actions/workflows/pr-merge.yml/badge.svg?branch=master&event=push
    :target: https://github.com/exasol/sqlalchemy-exasol/actions/workflows/pr-merge.yml
     :alt: CI Status

.. image:: https://img.shields.io/pypi/v/sqlalchemy_exasol
     :target: https://pypi.org/project/sqlalchemy_exasol/
     :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/sqlalchemy-exasol
    :target: https://pypi.org/project/sqlalchemy_exasol
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

.. image:: https://img.shields.io/badge/pylint-5.9-yellow
    :target: https://github.com/pylint-dev/pylint
    :alt: Pylint

.. image:: https://img.shields.io/pypi/l/sqlalchemy-exasol
     :target: https://opensource.org/license/BSD-2-Clause
     :alt: License

.. image:: https://img.shields.io/github/last-commit/exasol/sqlalchemy-exasol
     :target: https://pypi.org/project/sqlalchemy_exasol/
     :alt: Last Commit

.. image:: https://img.shields.io/pypi/dm/sqlalchemy-exasol
    :target: https://pypi.org/project/sqlalchemy_exasol
    :alt: PyPI - Downloads


Getting Started with SQLAlchemy-Exasol
--------------------------------------
SQLAlchemy-Exasol supports multiple dialects, primarily differentiated by whether they are ODBC or Websocket-based.

Choosing a Dialect
++++++++++++++++++

We recommend using the Websocket-based dialect due to its simplicity.
ODBC-based dialects demand a thorough understanding of (Unix)ODBC, and the setup is considerably more complex.

.. warning::

    The maintenance of Turbodbc & pyodbc support is currently paused, and it is planned to be phased out in future versions.


System Requirements
-------------------
- Exasol >= 7.1 (e.g. `docker-db <test_docker_image_>`_ or a `cloud instance <test_drive_>`_)
- Python >= 3.10

.. note::

   For ODBC-Based Dialects, additional libraries required for ODBC are necessary
   (for further details, checkout the `developer guide`_).

Features
--------

- SELECT, INSERT, UPDATE, DELETE statements

Getting Started
---------------

Check out sqlalchemy-exasols's [User Guide(https://exasol.github.io/sqlalchemy-exasol/master/user_guide.html) page for your first steps.

.. _developer guide: https://github.com/exasol/sqlalchemy-exasol/blob/master/doc/developer_guide/developer_guide.rst
.. _test_docker_image: https://github.com/exasol/docker-db
.. _odbc_driver: https://docs.exasol.com/db/latest/connect_exasol/drivers/odbc/odbc_linux.htm
.. _test_drive: https://cloud.exasol.com/signup
