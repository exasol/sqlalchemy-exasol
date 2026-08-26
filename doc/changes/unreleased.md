# Unreleased

## Summary

## Bugfixes

* #801: Corrected the bare `exa`
  SQLAlchemy entry point to load the default websocket dialect class directly. This
  keeps entry-point consumers such as Apache Superset working while preserving both
  `exa://` and `exa+websocket://` engine URLs.

## Documentation

* #781: Added Connection Pooling to the User Guide
* #797: Enhanced example and added documentation for listening to pool events
* #799: Added session reset to user guide section on Connection Pooling

## Refactorings

* #782: Added an integration test for creating a UDF incl. an example in the User Guide
* #784: Added test for exception to not reveal the password for connection pool
* #786: Added test for n+1 `connect()` to block
* #788: Enabled mypy type checks for tests
* #792: Added test to verify connections are reused by the connection pool
* #794: Added test to verify recycle timeout
