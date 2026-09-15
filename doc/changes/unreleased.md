# Unreleased

## Summary

In this patch release, websocket `TIMESTAMP` results preserve fractional seconds
and naive wall time. Wrapped PyExasol communication errors are recognized as
disconnects, allowing SQLAlchemy's pool pre-ping to replace stale connections on
first checkout, while server query/authentication errors remain connected and
in-flight SQL is not replayed.

## Bugfixes

* #807: Preserved fractional seconds and naive wall time in websocket `TIMESTAMP` results.
* #807: Recognized wrapped PyExasol communication errors as disconnects.
