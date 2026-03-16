# Unreleased

## Summary

This update fixes a bug that specifically impacted ORM sessions when flushing values to
pass IDs between linked SQLAlchemy tables. We discovered that the internal
`get_lastrowid` function has been off by one since the dialect’s inception (2015)
before Exasol's direct involvement, a bug that previously went unnoticed due to a gap
in test coverage. If you were affected, this discrepancy caused incorrect ID referencing
during data inserts, potentially breaking relational integrity in your sessions. We have
now fixed the logic to ensure the returned IDs are accurate and implemented new tests
that specifically validate row ID retrieval during ORM flushes.

## Refactoring

* #724: Updated to `exasol-toolbox` 6.0.0

## Bugfix

* #709: Fixed ORM session usage so that session IDs when flushed are not off by one
