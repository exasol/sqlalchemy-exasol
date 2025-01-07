# 4.6.0 — 2023-07-18

## 🚀 Feature

- Websocket based dialect have been stabilized and is officially supported now

    📘 Note: Inserting multiple empty row's, facilitating default settings currently isn't supported.

## 🐞 Fixed

- Fixed [prepared statements send the wrong types as parameters to the server](https://github.com/exasol/sqlalchemy-exasol/issues/341)
- Fixed [Various SQLA compliance tests are failing for the websocket based dialect](https://github.com/exasol/sqlalchemy-exasol/issues/342)

