# 7.2.0 - 2026-10-19

## Summary

In this minor release, the supported PyExasol version range has been widened to include PyExasol 3.0.0.
This version changes the default WebSocket DBAPI conversion so that values are
converted to Python types as early as possible, in accordance with PEP-249.

The following table describes values exposed by SQLAlchemy-Exasol through the
WebSocket DBAPI. The PyExasol version columns show the version-dependent
behavior seen by SQLAlchemy-Exasol; ``None`` is returned for ``NULL`` values
for all types.

| Exasol type                        | SQLAlchemy-Exasol with PyExasol < 3.0.0 | SQLAlchemy-Exasol with PyExasol >= 3.0.0 |
|------------------------------------|-----------------------------------------|------------------------------------------|
| ``BOOLEAN``                        | ``bool``                                | ``bool``                                 |
| ``CHAR``                           | ``str``                                 | ``str``                                  |
| ``DATE``                           | ``datetime.date``                       | ``datetime.date``                        |
| ``DECIMAL(p, 0)``                  | ``int``                                 | ``int``                                  |
| ``DECIMAL(p, s)`` where ``s > 0``  | ``decimal.Decimal``*                    | ``decimal.Decimal``                      |
| ``DOUBLE``                         | ``float``                               | ``float``                                |
| ``GEOMETRY``                       | ``str``                                 | ``str``                                  |
| ``HASHTYPE``                       | metadata ``KeyError`` (``str``)         | ``str``                                  |
| ``INTERVAL DAY TO SECOND``         | ``str``                                 | ``ExaTimeDelta``                         |
| ``INTERVAL YEAR TO MONTH``         | ``str``                                 | ``str``                                  |
| ``TIMESTAMP``                      | ``datetime.datetime``*                  | ``datetime.datetime``                    |
| ``TIMESTAMP WITH LOCAL TIME ZONE`` | ``str``                                 | ``datetime.datetime``                    |
| ``VARCHAR``                        | ``str``                                 | ``str``                                  |

\* PyExasol versions before 3.0.0 returned strings for these types, and
SQLAlchemy-Exasol converted those strings to the displayed Python types.

The SQLAlchemy column type declaration can change the Python type returned.
A native Exasol ``DECIMAL(p, 0)`` value is returned as
``int``. If the column is instead declared with SQLAlchemy's
``Numeric(18, 0)`` type, SQLAlchemy applies its decimal result processor and
returns ``decimal.Decimal``.

For additional details about the PyExasol 3.0.0 behavior changes, see the
[PyExasol 3.0.0 release notes](https://github.com/exasol/pyexasol/releases/tag/3.0.0).

## Features

* #833: Widened PyExasol range to include 3.x & improved datetime conversion for PyExasol < 3.x

## Refactorings

* #819: Adapted tests to work for all supported and future PyExasol versions
* #826: Added coverage for websocket's native types
* #829: Consolidated Timestamp type tests
* #822: Added test coverage for Exasol data types without first-class
  SQLAlchemy-Exasol type mappings

## Dependency Updates

### `main`

* Updated dependency `pyexasol:2.4.1` to `3.0.0`
