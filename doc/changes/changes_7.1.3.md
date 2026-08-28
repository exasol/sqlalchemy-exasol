# 7.1.3 - 2026-08-28

## Summary

This patch release fixes loading of the bare `exa` SQLAlchemy entry point,
expands the User Guide with connection pooling, pool events, and session reset
guidance, and adds test coverage for connection pooling and UDF creation.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability | Affected | Fixed in |
|------------|---------------|----------|----------|
| cryptography | PYSEC-2026-3552 | 49.0.0 | 50.0.0 |
| gitpython | GHSA-9rj7-rf2p-w77r | 3.1.57 | 3.1.58 |
| gitpython | GHSA-4gmw-gg2m-w46p | 3.1.57 | 3.1.58 |
| gitpython | CVE-2026-76217 | 3.1.57 | 3.1.58 |
| gitpython | GHSA-wvpp-8hx9-p66j | 3.1.57 | 3.1.58 |
| gitpython | GHSA-jm78-9fvv-mhgr | 3.1.57 | 3.1.58 |
| pip | PYSEC-2026-3721 | 26.1.2 | 26.2 |

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

## Dependency Updates

### `main`

* Updated dependency `packaging:26.2` to `26.3`
* Updated dependency `pyexasol:2.3.0` to `2.3.1`
* Updated dependency `sqlalchemy:2.0.51` to `2.0.52`

### `dev`

* Updated dependency `exasol-integration-test-docker-environment:6.4.1` to `6.5.1`
* Updated dependency `nox:2026.7.11` to `2026.8.10`
* Updated dependency `pydantic-settings:2.14.2` to `2.15.0`
* Updated dependency `pytest:9.0.3` to `9.1.1`
