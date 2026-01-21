# 5.2.0 - 2025-11-04

This release drops the support for Python 3.9 as this Python version has reached its [end-of-life](https://devguide.python.org/versions/) in 2025-10. In consequence, the release also fixes security vulnerabilities by updating the dependencies.

With this release, in the Websocket-based dialect, it is possible for users to pass `FINGERPRINT` into
the connection URL to take advantage of an additional security feature in PyExasol version
1.x.

```python
from sqlalchemy import create_engine
    url = "exa+websocket://A_USER:A_PASSWORD@192.168.1.2..8:1234/my_schema?FINGERPRINT=C70EB4DC0F62A3BF8FD7FF22D2EB2C489834958212AC12C867459AB86BE3A028"
    engine = create_engine(url)
    query = "select 42 from dual"
    with engine.connect() as con:
        result = con.execute(sql.text(query)).fetchall()
```

## Feature

- #612: Updated CI tests to run against Exasol DB versions 7.1.30, 8.34.0, and 2025.1.0. Dropped support for Python 3.9.
- #637: Added option to `exa-websocket` (Websocket-based dialect) to pass `FINGERPRINT` in the connection URL for additional security

## Refactoring

- #610: Altered string input into `Connection.execute()` to be handled properly with `sql.text()`
- #614: Altered params input into `Connection.execute()` to be handled properly with `dict`
- #616: Altered usage of MetaData which was binding to a connection to instead bind in the needed object or function
- #617: Enacted warning for the deprecation of the `autoload` parameter and requirement of `bind`
- #618: Switched DML & DDL executions from `engine.connect()` to `engine.begin()` usage
- #637: Updated dependency declaration to `pyexasol`

## Internal

- #558: Updated to poetry 2.1.2 & relocked dependencies to resolve CVE-2025-27516
- #548: Replaced pytest-exasol-itde with pytest-backend
- Relocked dependencies to resolve CVE-2025-43859
- #564: Replaced nox test:unit with that from exasol-toolbox
- Reformatted files to meet project specifications
- #588: Updated to exasol-toolbox 1.6.0 and relocked dependencies to resolve CVE-2025-50182, CVE-2025-50181, & CVE-2024-47081
- #605: Removed non-ASCII unicode from templates & relocked dependencies to resolve CVE-2025-8869 (pip -> transitive dependency)
- #640: Re-locked dependencies to resolve CVE-2025-8869 for transitive dependency pip

## Dependency Updates

### `main`
* Updated dependency `packaging:24.2` to `25.0`
* Updated dependency `pyexasol:0.27.0` to `1.2.1`
* Updated dependency `pyodbc:5.2.0` to `5.3.0`

### `dev`
* Removed dependency `black:25.1.0`
* Updated dependency `exasol-integration-test-docker-environment:3.4.0` to `4.3.0`
* Updated dependency `exasol-toolbox:0.20.0` to `1.12.0`
* Removed dependency `furo:2024.8.6`
* Removed dependency `isort:5.13.2`
* Removed dependency `mypy:1.15.0`
* Updated dependency `nox:2025.2.9` to `2025.10.16`
* Removed dependency `pre-commit:4.1.0`
* Removed dependency `pylint:3.3.4`
* Updated dependency `pyodbc:5.2.0` to `5.3.0`
* Removed dependency `pytest-cov:6.0.0`
* Added dependency `pytest-exasol-backend:1.2.2`
* Removed dependency `pytest-exasol-itde:0.2.1`
* Removed dependency `pytest-history:0.3.0`
* Removed dependency `pyupgrade:3.19.1`
* Removed dependency `sphinx:7.4.7`
* Removed dependency `sphinx-copybutton:0.5.2`
* Removed dependency `urlscan:1.0.6`
