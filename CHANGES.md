# unreleased
* Turbodbc support uses buffer size based on memory budget
  instead of a fixed number of rows.
* Turbodbc support requires turbodbc>=0.4.1

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
