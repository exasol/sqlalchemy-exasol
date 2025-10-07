# Unreleased

Due to an EOL for [Python 3.9 in 2025-10](https://devguide.python.org/versions/), we dropped support for it.
This allows us to use the latest dependencies, which do not have open vulnerabilities.

## Feature

- #612: Updated CI tests to run against Exasol DB versions 7.1.30, 8.34.0, and 2025.1.0. Dropped support for Python 3.9.

## Refactoring

- #610: Altered string input into `Connection.execute()` to be handled properly with `sql.text()`
- #614: Altered params input into `Connection.execute()` to be handled properly with `dict`
- #616: Altered usage of MetaData which was binding to a connection to instead bind in the needed object or function

## Internal

- #558: Updated to poetry 2.1.2 & relocked dependencies to resolve CVE-2025-27516
- #548: Replaced pytest-exasol-itde with pytest-backend
- Relocked dependencies to resolve CVE-2025-43859
- #564: Replaced nox test:unit with that from exasol-toolbox
- Reformatted files to meet project specifications
- #588: Updated to exasol-toolbox 1.6.0 and relocked dependencies to resolve CVE-2025-50182, CVE-2025-50181, & CVE-2024-47081
- #605: Removed non-ASCII unicode from templates & relocked dependencies to resolve CVE-2025-8869 (pip -> transitive dependency)
