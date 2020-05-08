# 2.0.10
* bumped SQLAlchemy to 1.3.16
* bumped six to 1.14.0
* bumped pyodbc to 4.0.30

# 2.0.9
* bumped SQLAlchemy to 1.3.10
* merge supports computed columns (contribution by @vamega)

# 2.0.8
* added new EXASOL keywords (contribution from @vamega)
* added MERGE statement to auto commit heuristic (contribution from @vamega)
* switched to API token for PyPi upload

# 2.0.7
* bumped travis build system to Ubuntu bionic (~Debian 9)
* bumped SQLAlchemy to 1.3.8

# 2.0.6
* fixed bug in reflection of CHAR colums (missing length). Contribution from @vamega
* fixed bug in rendering of SQL statements with common table expressions (CTE). Contribution from @vamega
* added support for empty set expressions required by new SQLA tests
* removed deprecated setting of 'convert_unicode' on engine
* bumped PyODBC (4.0.27) and SQLAlchemy (1.3.6) dependencies

# 2.0.5
* bumped to SQLAlchemy 1.2.18
* fixed bug in server version string parsing (turbodbc)

# 2.0.4
* Use setuptools_scm to get proper development package versions
* bumped pyodbc to 4.0.24
* Handle string parameters in delete correctly in Python 3

# 2.0.3
* Pass the autocommit parameter when specified also to turodbc.
* bumped to SQLAlchemy 1.2.10

# 2.0.2
* version left out

# 2.0.1
* dropped EXASOL 5 from integration tests
* bumped to SQLAlchemy 1.2.8
* Support the turbodbc parameters `varchar_max_character_limit`, `prefer_unicode`,
  `large_decimals_as_64_bit_types`, and `limit_varchar_results_to_max`.

# 2.0.0
* BREAKING CHANGE: default driver name removed from dialect. The driver must now be explicitly
  specified. Either in the DSN or in the connection string using the
  optional 'driver' parameter (e.g. appending &driver=EXAODBC to connection URL)
* bumped to SQLAlchemy 1.2.0, pyodbc 4.0.21

# 1.3.2
* bumped to SQLAlchemy 1.1.14
* switched to travis builds without root, bumped tests to Python 3.6

# 1.3.1
* bumped to SQLAlchemy 1.1.13
* add raw_sql to util.py for debuging

# 1.3.0
* added EXASOL 6 driver (6.0.2)
* Fixed #53 - TRUNCATE statements now autocommited (if autocommit = True)
* bumped SQLAlchemy to 1.1.12

# 1.2.5
* bumped to version pyodbc 4.0.17
* added EXASOL 6 to build matrix
* adjusted list of reserved keywords to EXASOL 6
* kicked out EXASOL 4 driver

# 1.2.4
* fixed bug introduced by typo in base.py:454

# 1.2.3
* missing kw arg in limit_clause (contribution from sroecker)
* bumped SQLAlchemy to 1.1.11
* fixed bug with incorrect handling of case insensitive names (lower case in SQLA, upper case in EXASOL)
* fixed bug in lookup of default schema name to include schema provided in connection url
* reverted EXAExecutionContext.executemany to default 'False' to fix failing
  test in SQLAlchemy 1.1.10

# 1.2.2
* fix for failing upload of build results to pypi

# 1.2.1
* Fixed ODBC Driver name that is to be used
* Use unicode on osx for turbodbc fixes #63

# 1.2.0
* Turbodbc support uses buffer size based on memory budget
  instead of a fixed number of rows.
* Turbodbc support requires turbodbc>=0.4.1
* Add Support for Python 3.6

# 1.1.1
* Upgrade sqlalchemy version requirement to 1.x; use 1.1.1 in tests

# 1.1.0
* Add support for the [turbodbc](https://github.com/blue-yonder/turbodbc) driver

NOTE: dropped EXASOL 4 support

# 1.0.3
* Reconnect after socket closed

# 1.0.2
* fix Unicode Problems for OSX/Darwin
* better DSN handling
* add supports_native_decimal Flag

# 1.0.1
* add OFFSET Support for Exasol 5.X
* add Tests for Python 3.5

# 1.0.0
* upgrade to sqlalchemy 1.0.x (incompatible changes drop support for older sqlalchemy versions)

# 0.9.3
* change execute behaviour for deletes as fixed in 0.9.2 for updates (#36)

# 0.9.2
* change execute behaviour for updates fixes #36

# 0.9.1
* support for DISTRIBUTE BY table constraints

# 0.9.0
* Bug Fix: conversion to uppercase in connection parameters (https://github.com/blue-yonder/sqlalchemy_exasol/commit/a2b06ea0933a47e5dadf853f54bd9a28f202b16e)
* Implemented is_disconnect in driver to mark connections in pool as closed to prevent reuse
* Use bulk reflection per schema and imporoved caching for inspection
* Added EXASolution 5.x to the build matrix
* Added some documentation on how to setup the integration test against the EXASOL hosted test db

# 0.8.5
* default schema is set to 'SYS' to create reasonable reflections
* fixes for Python 3.4 support
* Python 3.4 test included in Travis build

# 0.8.4
* reduce dependency version to python package six from >=1.7 to >=1.5

# 0.8.3
* fix versioneer build parameter in setup.py to enable pip install

# 0.8.2
* added missing README.rst

# 0.8.1

* updated repository url
* p3k support - contribution by iadrich

# 0.8.0

* added support for SQL MERGE
* upgraded to SQLA 0.9.x (build requires >= 0.9.6)
* bug fixes
    * incorrect quoting of identifiers with leading _
    * incorrect implementation for retrieving last generated PK (for auto inc columns)

# 0.7.5

* switched to versioneer

# 0.7.4

* changed README from md to rst to display reasonable content on pypi

# 0.7.0

* First version of the SQLAlchemy EXASOL dialect released under BSD license
* a lot of minor bug fixes to pass the SQLAlchemy test suite
