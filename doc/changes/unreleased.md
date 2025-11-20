# Unreleased

In this release, the ODBC-based dialects pyodbc and Turbodbc were dropped. Please
switch over to using the websocket dialect. Connection
strings should be altered to start with `exa+websocket://`.

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
