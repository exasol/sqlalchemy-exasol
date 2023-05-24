.. _changelog-unreleased:

Unreleased
==========

.. _changelog-4.5.0:

4.5.0 — 2023-05-24
==================
* Added Beta version of websocket based dialect

     **🚨 Attention:**

        This feature is currently in Beta, therefore it should not be used in production.
        We also recommend to have a look into the known issues, before you start using it.

        If you encounter any problem, please `create an issue <https://github.com/exasol/sqlalchemy-exasol/issues/new?assignees=&labels=bug&projects=&template=bug.md&title=%F0%9F%90%9E+%3CInsert+Title%3E>`_.
        With your feedback, we will be able stabilize this feature more quickly.


.. _changelog-4.4.0:

4.4.0 — 2023-05-16
==================

 **🚨 Attention:**

    The turbodbc dependency was pinned to *4.5.4* due to issues with newer versions.

    Failing tests in the SQLA compliance test suite, in regard to the turbodbc dialect
    won't be addressed until explicitly required/requested by users.

    Note: It is also very likely that turbodbc support will be dropped in future versions.

🐞 Fixed
--------

* Fixed invalid implicit autocommit behaviour, for details see `<Issue-https://github.com/exasol/sqlalchemy-exasol/issues/335>`_

✨ Added
--------

* Added websocket based dbapi2 compliant database driver

🔧 Changed
----------

* Updated pytest
* Updated Dependencies
* Loosened version constraints on 'packaging' dependency
* Loosened dev dependency constraints

🧰 Internal
-----------
* Changed changelog workflow

    - Removed scriv
    - Added unreleased section to track unreleased changes

* Simplified workflows by factoring out python & poetry setup into an action
* Added a internal category to the changelog fragment template
* Added manual trigger for the gh-pages workflow
* Removed workaround for outdated DB versions
  (for further details see https://github.com/exasol/sqlalchemy-exasol/issues/5)
* Added exasol-integration-test-docker-environment as dev dependency

.. _changelog-4.0.0:

4.0.0 — 2022-12-01
==================

✨ Added
--------

* Added support for SQLA 1.4

    .. warning::
        This upgrade is not backwards compatible with SQLA < 1.4

    .. warning::

        This version may impact the performance (see also `SQLAlchemy docs <https://docs.sqlalchemy.org/en/14/faq/performance.html#why-is-my-application-slow-after-upgrading-to-1-4-and-or-2-x>`_).
        If you are not willing or able to pay those potential performance hits, you should wait until the `tracking-issue #190 <https://github.com/exasol/sqlalchemy-exasol/issues/190>`_
        is resolved.


🗑️ Removed
----------

* Removed custom merge statement

  (If we will be notified, that someone depends on this feature, we are open to add it again.)

🔐 Security
-----------

- Evaluated CVE-2022-42969
     - CVE will be silenced
     - The affected code is not used by our project itself,
       nor by the dependencies pulling in the vulnerable library.

        Checked dependencies:

        * Nox (Code search)
        * Pytest (Code search + `tracking-issue #10392 <https://github.com/pytest-dev/pytest/issues/10392>`_)

🔧 Changed
----------

- Updated all dependencies

🐞 Fixed
---------

- Fixed link to project documentation


.. _changelog-3.2.1:

3.2.2 — 2022-08-12
==================

✨ Added
--------
- Added turbodbc support 
    * Re-enabled with new minimum base version 4.5.4
- Added additional information to README
    * License information (badge)
    * Code formatter(s) in use (black, isort)
    * Linting score of the project

🔧 Changed
----------
- Changed changelog format
  * Changelog now can be found in the file CHANGELOG.rst
- Reworked and restructured project documentation

🗑️ Removed
----------
-  Removed markdown based changelog


.. _changelog-3.1.1:

3.1.1 — 2022-07-21
==================

✨ Added
--------
- Added new exasol odbc driver 7.1.11
- Added additional badges for to improve project status overview

🔧 Changed
----------
- Updated databases for testing to 7.1.9 and 7.0.18
- Updated pyodbc dependency from 4.0.32 to 4.0.34

🐞 Fixed
--------
- Fixed CI/CD build and publish target
- Fixed CI/CD to run tests against all configured databases


.. _changelog-3.0.0:

3.0.0 — 2022-07-14
==================

🗑️ Removed
----------
- The support of the turbodbc feature has been suspended, until the following issues have been addressed
    * https://github.com/blue-yonder/turbodbc/issues/358
    * https://github.com/exasol/sqlalchemy-exasol/issues/146
    * Note: If you depend on turbodbc we suggest you to use the latest version supporting it (2.4.0)

- Dropped python 3.7 support
  * If you still depend on python 3.7 use the 2.x version line
- Dropped conda forge support


.. _changelog-2.4.0:

2.4.0 — 2022-05-19
==================

🗑️ Removed
----------
- Removed odbc specific functionality from base dialect and moved it to the pyodbc dialect
- Removed remaining python2 compatibility artifacts and switches
- Dropped support for python versions < 3.7

🐞 Fixed
--------
- Fixed bug when accessing underlying odbc connection while using NullPool based engine
  Note: This addresses the superset `issue-20105 <https://github.com/apache/superset/issues/20105>`_


.. _changelog-2.3.0:

2.3.0 — 2022-04-13
==================

🗑️ Removed
----------
- Removed outdated documentation and resources
- Dropped python 2.7 support

🔧 Changed
----------
* Update supported versions of EXASOL DB to 7.1.6 and 7.0.16
* Update supported python versions to 3.6, 3.7, 3.8, 3.9
* Bumped SQLAlchemy dependency to 1.3.24
* Bumped pyodbc dependency to 4.0.32
* Updated documentation to reflect the latest version changes etc.
* Updated maintainer and contact information

🐞 Fixed
--------
* Fixed bug regarding maximum identifier length
* Fixed bug with custom translate maps
* Fixed bug regarding non existent error code mappings for EXASOL specific odbc error codes


.. _changelog-2.2.0:

2.2.0 — 2020-09-02
==================

🔧 Changed
----------
- Updated dependencies

🐞 Fixed
--------
- Fixed performance problems for large tables/databases. For more details see `PR <https://github.com/blue-yonder/sqlalchemy_exasol/pull/101>`_


.. _changelog-2.1.0:

2.1.0 — 2020-05-28
==================

🔧 Changed
----------
- Updated documentation (README.rst and INTEGRATION_TEST.md)
- Updated dependencies
- Replaced metadata queries with ODBC metadata to avoid deadlocks


.. _changelog-2.0.10:

2.0.10 — 2020-05-08
===================

🔧 Changed
----------
- Updated SQLAlchemy dependency to 1.3.16
- Updated six dependency to 1.14.0
- Updated pyodbc dependency to 4.0.30


.. _changelog-2.0.9:

2.0.9 — 2019-10-18
===================

✨ Added
--------
- Add support for computed columns to merge (contribution by @vamega)

🔧 Changed
----------
- Updated SQLAlchemy dependency to 1.3.10


.. _changelog-2.0.8:

2.0.8 — 2019-10-07
===================

✨ Added
--------
- Added new EXASOL keywords (contribution from @vamega)
- Added MERGE statement to auto commit heuristic (contribution from @vamega)


.. _changelog-2.0.7:

2.0.7 — 2019-10-01
===================

🔧 Changed
----------
- Updated SQLAlchemy dependency to 1.3.8


.. _changelog-2.0.6:

2.0.6 — 2019-08-12
===================

🗑️ Removed
----------
- Removed deprecated setting of 'convert_unicode' on engine

✨ Added
--------
- Added support for empty set expressions required by new SQLA tests

🔧 Changed
----------
- Updated PyODBC dependency to 4.0.27
- Updated SQLAlchemy dependency to 1.3.6

🐞 Fixed
--------
- Fixed bug in reflection of CHAR colums (missing length). Contribution from @vamega
- Fixed bug in rendering of SQL statements with common table expressions (CTE). Contribution from @vamega


.. _changelog-2.0.5:

2.0.5 — 2019-05-03
===================

🔧 Changed
----------
- Updated SQLAlchemy dependency to 1.2.18

🐞 Fixed
--------
- Fixed bug in server version string parsing (turbodbc)


.. _changelog-2.0.4:

2.0.4 — 2018-10-16
===================

🔧 Changed
----------
- Updated pyodbc dependency to 4.0.24

🐞 Fixed
--------
- Fix string parameters in delete when using Python 3


.. _changelog-2.0.3:

2.0.3 — 2018-08-02
===================

🔧 Changed
----------
- Update SQLAlchemy dependency to 1.2.10

🐞 Fixed
--------
- Pass the autocommit parameter when specified also to turodbc.


.. _changelog-2.0.1:

2.0.1 — 2018-06-28
===================

🗑️ Removed
----------
- Dropped EXASOL 5 support

✨ Added
--------
- Added support for the turbodbc parameters `varchar_max_character_limit`, `prefer_unicode`,
  `large_decimals_as_64_bit_types`, and `limit_varchar_results_to_max`.

🔧 Changed
----------
- Update SQLAlchemy dependency to 1.2.8


.. _changelog-2.0.0:

2.0.0 — 2018-01-09
===================

🔧 Changed
----------
- BREAKING CHANGE: default driver name removed from dialect. The driver must now be explicitly
  specified. Either in the DSN or in the connection string using the
  optional 'driver' parameter (e.g. appending &driver=EXAODBC to connection URL)
- Updated SQLAlchemy dependency to 1.2.0
- Updated pyodbc dependency to 4.0.21


.. _changelog-1.3.2:

1.3.2 — 2017-10-15
===================

🗑️ Removed
----------
- Dropped support for Python3 version < Python 3.6

🔧 Changed
----------
- Updated SQLAlchemy dependency to 1.1.14


.. _changelog-1.3.1:

1.3.1 — 2017-08-16
===================

✨ Added
--------
- Added `raw_sql` to util.py for debugging

🔧 Changed
----------
- Updated SQLAlchemy dependency to 1.1.13


.. _changelog-1.3.0:

1.3.0 — 2017-08-02
===================

✨ Added
--------
- Added EXASOL 6 driver (6.0.2)

🔧 Changed
----------
- Updated SQLAlchemy dependency to 1.1.12

🐞 Fixed
--------
- Fixed issue #53 - TRUNCATE statements now autocommited (if autocommit = True)


.. _changelog-1.2.5:

1.2.5 — 2017-08-02
===================

🗑️ Removed
----------
- Removed support for EXASOL 4 driver

✨ Added
--------
- Added support for EXASOL 6

🔧 Changed
----------
- Updated pyodbc dependency to 4.0.17
- Adjusted list of reserved keywords in respect to EXASOL 6


.. _changelog-1.2.4:

1.2.4 — 2017-06-26
===================

🐞 Fixed
--------
- Fixed bug introduced by typo in base.py:454


.. _changelog-1.2.3:

1.2.3 — 2017-06-20
===================

✨ Added
--------
- Added missing kw arg in limit_clause (contribution from sroecker)

🔧 Changed
----------
- Updated SQLAlchemy dependency to 1.1.11
- Changed EXAExecutionContext.executemany to default 'False'

🐞 Fixed
--------
- Fixed bug with incorrect handling of case insensitive names (lower case in SQLA, upper case in EXASOL)
- Fixed bug in lookup of default schema name to include schema provided in connection url


.. _changelog-1.2.2:

1.2.2 — 2017-05-29
===================

🐞 Fixed
--------
- Fixed failing upload of build results to pypi


.. _changelog-1.2.1:

1.2.1 — 2017-05-25
===================

🐞 Fixed
--------
- Fixed ODBC Driver name that is to be used
- Use unicode on osx for turbodbc fixes #63


.. _changelog-1.2.0:

1.2.0 — 2017-04-04
===================

✨ Added
--------
- Added Support for Python 3.6

🔧 Changed
----------
- Turbodbc support uses buffer size based on memory budget
  instead of a fixed number of rows.
- Turbodbc support requires turbodbc>=0.4.1


.. _changelog-1.1.1:

1.1.1 — 2016-10-14
===================

🔧 Changed
----------
- Upgrade sqlalchemy test dependency to 1.1.1


.. _changelog-1.1.0:

1.1.0 — 2016-07-15
===================

🗑️ Removed
----------
- Dropped EXASOL 4 support

✨ Added
--------
- Add support for the `turbodbc <https://github.com/blue-yonder/turbodbc>`_ driver


.. _changelog-1.0.3:

1.0.3 — 2016-04-14
===================

🔧 Changed
----------
- Reconnect after socket closed


.. _changelog-1.0.2:

1.0.2 — 2016-03-12
===================

✨ Added
--------
- Added supports_native_decimal Flag

🔧 Changed
----------
- Improved DSN handling

🐞 Fixed
--------
- Fixed Unicode Problems for OSX/Darwin


.. _changelog-1.0.1:

1.0.1 — 2015-03-21
===================

✨ Added
--------
- Added OFFSET Support for Exasol 5.X
- Added Tests for Python 3.5


.. _changelog-1.0.0:

1.0.0 — 2015-05-15
===================

🗑️ Removed
----------
- Dropped support for sqlalchemy versions < 1.0.x

🔧 Changed
----------
- Update sqlalchemy dependency to 1.0.x


.. _changelog-0.9.3:

0.9.3 — 2015-05-13
===================

🔧 Changed
----------
- Changed execute behaviour for deletes as fixed in 0.9.2 for updates (#36)


.. _changelog-0.9.2:

0.9.2 — 2015-05-06
===================

🐞 Fixed
----------
- Changed execute behaviour for updates fixes #36


.. _changelog-0.9.1:

0.9.1 — 2015-01-29
===================

✨ Added
--------
- Added support for DISTRIBUTE BY table constraints


.. _changelog-0.9.0:

0.9.0 — 2015-01-26
===================

✨ Added
--------
- Added support for EXASolution 5.x
- Added documentation on how to setup the integration test against the EXASOL hosted test db

🔧 Changed
----------
- Mark connection in pool as closed to prevent reuse
- Use bulk reflection per schema and improved caching for inspection

🐞 Fixed
----------
- Fixed conversion to uppercase in connection parameters


.. _changelog-0.8.5:

0.8.5 — 2014-07-31
===================

✨ Added
--------
- Added Python 3.4 test

🔧 Changed
----------
- Set default schema to 'SYS' to create reasonable reflections


.. _changelog-0.8.4:

0.8.4 — 2014-07-30
===================

🔧 Changed
----------
- Downgrade six dependency selector to >=1.5


.. _changelog-0.8.3:

0.8.3 — 2014-07-18
===================

🐞 Fixed
--------
- Fixed versioneer build parameter in setup.py to enable pip install


.. _changelog-0.8.2:

0.8.2 — 2014-07-17
===================

✨ Added
--------
- Added README


.. _changelog-0.8.1:

0.8.1 — 2014-06-26
===================

✨ Added
--------
- Added p3k support - contribution by iadrich

🔧 Changed
----------
- Updated repository url


.. _changelog-0.8.0:

0.8.0 — 2014-06-26
===================

✨ Added
--------
- Added support for SQL MERGE

🔧 Changed
----------
- Updated SQLA dependency selector to 0.9.x (build requires >= 0.9.6)

🐞 Fixed
--------
- Fixed incorrect quoting of identifiers with leading _
- Fixed incorrect implementation for retrieving last generated PK (for auto inc columns)


.. _changelog-0.7.5:

0.7.5 — 2014-05-08
===================

🔧 Changed
----------
- Switched to versioneer


.. _changelog-0.7.4:

0.7.4 — 2014-04-01
===================

🔧 Changed
----------
- changed README from md to rst to display reasonable content on pypi


.. _changelog-0.7.0:

0.7.0 — 2014-03-28
===================

✨ Added
--------
- Added first version of the SQLAlchemy EXASOL dialect (released under BSD license)
