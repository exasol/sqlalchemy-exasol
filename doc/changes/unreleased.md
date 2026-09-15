# Unreleased

## Summary

In this patch release, `EXTRACT` compilation is fixed. The `extract_map` override in
`EXACompiler`, copied from the SQLite dialect, rendered C `strftime` format codes such
as `EXTRACT(%Y FROM c)` instead of SQL date parts. The six fields Exasol supports,
`year`, `month`, `day`, `hour`, `minute` and `second`, now render correctly as
`EXTRACT(year FROM c)`. Fields Exasol's `EXTRACT` does not support, such as `week`,
`dow`, `doy`, `quarter` and `epoch`, now raise `CompileError` at compile time instead
of failing on the server with a syntax error.

## Bugfixes

* #810: Fixed `EXTRACT` compilation to render SQL date parts and reject fields Exasol
  does not support
