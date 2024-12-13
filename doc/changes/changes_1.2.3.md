# 1.2.3 — 2017-06-20

## ✨ Added

- Added missing kw arg in limit_clause (contribution from sroecker)

## 🔧 Changed

- Updated SQLAlchemy dependency to 1.1.11
- Changed EXAExecutionContext.executemany to default `False`

## 🐞 Fixed

- Fixed bug with incorrect handling of case insensitive names (lower case in SQLA, upper case in EXASOL)
- Fixed bug in lookup of default schema name to include schema provided in connection url

