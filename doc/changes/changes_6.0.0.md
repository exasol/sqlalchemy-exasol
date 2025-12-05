# 6.0.0 - 2025-12-05

In this major release, `sqlachemy-exasol` has been migrated to the SQLAlchemy 2.0 API
and conventions. The focus of the migration was preserving existing feature parity.
Thus, new features added in the SQLAlchemy 2.0 API may not work as expected.
If such features are important to your team or if you experience other issues, please open
an [issue](https://github.com/exasol/sqlalchemy-exasol/issues). Note that this migration
is a **breaking change** and action will need to be taken by your team to make
your code compatible with `sqlalchemy-exasol==6.0.0`.

The migration to SQLAlchemy 2.0 allows users to benefit from continued security support, performance
improvements, modern typing support, and additional features. For details
on what SQLAlchemy 2.0 brings and which changes are needed in your projects, please
check out the following links:
* [What's New in 2.0](https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html)
* [Major Migration Guide for 2.0](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)

Additionally, the ODBC-based dialects pyodbc and Turbodbc, which had been marked as
deprecated, were dropped. Please switch over to using the websocket dialect.
Connection strings should be altered to start with `exa+websocket://`.

## Refactoring

- #621: Added `future=true` to `create_engine` to use the 2.0 API
- #623: Started switch to `sqlalchemy` 2.x (CI tested with 2.0.43)
  - All unit, `exasol`, and `regression` tests are working
  - Several tests from `sqlalchemy` are failing, have been marked as skipped, and require investigation
  - Reinstated the ArgSignatureTest which ensures that all visit_XYZ() in `_sql.Compiler` subclasses have `**kw`
- #626: Reinstated `sqlalchemy` tests:
  - `TrueDivTest.test_floordiv_integer` and `TrueDivTest.test_floordiv_integer_bound` by providing an override in `EXACompiler.visit_floordiv_binary`
  - `TrueDivTest.test_truediv_numeric` by providing `ExaDecimal` to the `EXADialect_pyodbc.colspecs` list
  - a few tests from `ComponentReflectionTest` as `define_reflected_tables` is overridden based on what Exasol supports
- #631: Updated `EXADialect.has_table` to search for both tables and views, fixed passing of schema=None to dialect methods, and reinstated `sqlalchemy` tests:
  - `ReturningGuardsTest` are used to indicate that the Exasol dialect, which does not natively support the [RETURNING clause](https://docs.sqlalchemy.org/en/20/glossary.html#term-RETURNING), is set up per the API specifications
  - `ComponentReflectionTest.test_not_existing_table` is used to indicate that specific `EXADialect` methods (i.e. `get_columns`) check to see if the requested table/view exists and if not, they will now toss a `NoSuchTableError` exception
- #403: Dropped support for Turbodbc
- #404: Dropped support for pyodbc
- #654: Reinstated `sqlalchemy` tests after minor modifications to work for Exasol:
  - `ComponentReflectionTest.test_get_multi_columns`
  - `ComponentReflectionTest.test_get_multi_foreign_keys`
  - `ComponentReflectionTest.test_get_multi_pk_constraint`
  - `ComponentReflectionTest.test_get_view_definition_does_not_exist`
- #652: Reinstated `sqlalchemy` tests after minor modifications to work for Exasol:
  - `HasTableTest.test_has_table_cache`
  - `RowCountTest.test_non_rowcount_scenarios_no_raise`
- #658: Updated to `exasol-toolbox` 3.0.0

## Documentation
- #660: Updated User Guide
  - Added Getting Started, Security, & Engine Configuration pages
  - Cleaned up index and README.rst
- #663: Updated developer documentation
- #653: Updated User Guide for accessing Exasol SaaS instances.

## Dependency Updates

### `main`
* Updated dependency `pyexasol:1.2.1` to `1.3.0`
* Removed dependency `pyodbc:5.3.0`
* Updated dependency `sqlalchemy:1.4.54` to `2.0.44`
* Removed dependency `turbodbc:4.5.4`

### `dev`
* Updated dependency `exasol-integration-test-docker-environment:4.3.0` to `4.4.1`
* Updated dependency `exasol-toolbox:1.12.0` to `3.0.0`
* Updated dependency `nox:2025.10.16` to `2025.11.12`
* Removed dependency `pyodbc:5.3.0`
