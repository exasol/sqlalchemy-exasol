# 2.4.0 — 2022-05-19

## 🗑️ Removed

- Removed odbc specific functionality from base dialect and moved it to the pyodbc dialect
- Removed remaining python2 compatibility artifacts and switches
- Dropped support for python versions `< 3.7`

## 🐞 Fixed

- Fixed bug when accessing underlying odbc connection while using NullPool based engine
  Note: This addresses the superset [issue-20105](https://github.com/apache/superset/issues/20105)

