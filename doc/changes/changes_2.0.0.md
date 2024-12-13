# 2.0.0 — 2018-01-09

## 🔧 Changed

- BREAKING CHANGE: default driver name removed from dialect. The driver must now be explicitly
  specified. Either in the DSN or in the connection string using the
  optional 'driver' parameter (e.g. appending &driver=EXAODBC to connection URL)
- Updated SQLAlchemy dependency to 1.2.0
- Updated pyodbc dependency to 4.0.21


