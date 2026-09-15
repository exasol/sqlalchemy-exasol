# Unreleased

## Summary

## Bugfixes

* #<issue>: Fixed `EXTRACT` compilation, which rendered C `strftime` format codes such as
  `EXTRACT(%Y FROM c)` instead of SQL date parts like `EXTRACT(year FROM c)`. The
  `extract_map` override in `EXACompiler`, copied from the SQLite dialect, was removed
  so the base compiler passes the field name through unchanged.
