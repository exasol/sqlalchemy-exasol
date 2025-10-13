# Unreleased

Due to an EOL for [Python 3.9 in 2025-10](https://devguide.python.org/versions/), we dropped support for it.
This allows us to use the latest dependencies, which do not have open vulnerabilities.

## Feature

- #612: Updated CI tests to run against Exasol DB versions 7.1.30, 8.34.0, and 2025.1.0. Dropped support for Python 3.9.

## Refactoring

- #610: Altered string input into `Connection.execute()` to be handled properly with `sql.text()`
- #614: Altered params input into `Connection.execute()` to be handled properly with `dict`
- #616: Altered usage of MetaData which was binding to a connection to instead bind in the needed object or function
- #617: Enacted warning for the deprecation of the `autoload` parameter and requirement of `bind`
- #618: Switched DML & DDL executions from `engine.connect()` to `engine.begin()` usage
- #621: Added `future=true` to `create_engine` to use the 2.0 API
- #623: Started switch to `sqlalchemy` 2.x (CI tested with 2.0.43)
  - All unit, `exasol`, and `regression` tests are working
  - Several tests from `sqlalchemy` are failing, have been marked as skipped, and require investigation
  - Reinstated the ArgSignatureTest which ensures that all visit_XYZ() in `_sql.Compiler` subclasses have `**kw`
- #626: Reinstated `sqlalchemy` tests:
  - `TrueDivTest.test_floordiv_integer` and `TrueDivTest.test_floordiv_integer_bound` by providing an override in `EXACompiler.visit_floordiv_binary`
  - `TrueDivTest.test_truediv_numeric` by providing `ExaDecimal` to the `EXADialect_pyodbc.colspecs` list
  - a few tests from `ComponentReflectionTest` as `define_reflected_tables` is overridden based on what Exasol supports

## Internal

- #558: Updated to poetry 2.1.2 & relocked dependencies to resolve CVE-2025-27516
- #548: Replaced pytest-exasol-itde with pytest-backend
- Relocked dependencies to resolve CVE-2025-43859
- #564: Replaced nox test:unit with that from exasol-toolbox
- Reformatted files to meet project specifications
- #588: Updated to exasol-toolbox 1.6.0 and relocked dependencies to resolve CVE-2025-50182, CVE-2025-50181, & CVE-2024-47081
- #605: Removed non-ASCII unicode from templates & relocked dependencies to resolve CVE-2025-8869 (pip -> transitive dependency)
