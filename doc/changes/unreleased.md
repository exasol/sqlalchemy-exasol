# Unreleased

## Summary

## Bug fixes

* Preserve fractional seconds and naive wall time in websocket TIMESTAMP results.
* Recognize wrapped PyExasol communication errors as disconnects, enabling
  SQLAlchemy's pool pre-ping to replace stale connections on the first checkout.
  Server query/authentication errors are not disconnects; in-flight SQL is not replayed.

See issue #807.
