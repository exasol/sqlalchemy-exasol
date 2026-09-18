# Unreleased

## Summary

In this patch release, three issues were fixed:

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

## Bugfixes

* #810: Fixed `EXTRACT` compilation to render SQL date parts and reject fields Exasol
  does not support
* #807: Preserved fractional seconds and naive wall time in websocket `TIMESTAMP` results.
* #807: Recognized wrapped PyExasol communication errors as disconnects.
