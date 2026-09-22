# 7.1.4 - 2026-09-22

## Summary

In this patch release, four issues were fixed:

* `EXTRACT` compilation is fixed. The previous `extract_map` override in
  `EXACompiler` was copied from the SQLite dialect and incorrectly rendered C
  `strftime` format codes (e.g. `EXTRACT(%Y FROM c)`) instead of SQL date parts.
  The six fields Exasol supports, `year`, `month`, `day`, `hour`, `minute` and
  `second`, now render correctly as `EXTRACT(year FROM c)`. Fields Exasol's
  `EXTRACT` does not support, such as `week`, `dow`, `doy`, `quarter` and `epoch`,
  now raise a `CompileError` at compile time instead of failing on the server
  with a syntax error.

* Websocket `TIMESTAMP` results have been corrected to preserve fractional seconds and naive wall time.

* Wrapped PyExasol communication errors are now correctly recognized as disconnects,
  allowing SQLAlchemy's pool pre-ping to replace stale connections on first checkout,
  while server query/authentication errors remain connected and in-flight SQL is
  not replayed.

* PyExasol exception handling has been aligned with the DB-API exception mapping
  introduced in PyExasol 2.4.1, while retaining compatibility with older supported
  PyExasol versions.
  * `ExaAuthError` and `ExaRequestError` are now mapped to `DatabaseError` instead
    of `OperationalError`, and `ExaConcurrencyError` is now mapped to
    `InterfaceError`.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability | Affected | Fixed in |
|------------|---------------|----------|----------|
| gitpython | PYSEC-2026-3983 | 3.1.59 | 3.1.60 |
| gitpython | PYSEC-2026-3984 | 3.1.59 | 3.1.60 |
| gitpython | PYSEC-2026-3982 | 3.1.59 | 3.1.60 |

## Bugfixes

* #810: Fixed `EXTRACT` compilation to render SQL date parts and reject fields Exasol
  does not support
* #807: Preserved fractional seconds and naive wall time in websocket `TIMESTAMP` results.
* #807: Recognized wrapped PyExasol communication errors as disconnects.
* #812: Aligned PyExasol exception handling with the DB-API exception mapping provided
  by PyExasol 2.4.1 and newer.

## Dependency Updates

### `main`

* Updated dependency `pyexasol:2.3.1` to `2.4.1`
* Updated dependency `sqlalchemy:2.0.52` to `2.0.54`

### `dev`

* Updated dependency `exasol-toolbox:10.4.0` to `11.0.0`
* Updated dependency `nox:2026.8.10` to `2026.8.17`
* Updated dependency `pydantic:2.13.4` to `2.13.5`
