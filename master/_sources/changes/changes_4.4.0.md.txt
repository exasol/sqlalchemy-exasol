# 4.4.0 — 2023-05-16

**🚨 Attention:**

The turbodbc dependency was pinned to `4.5.4` due to issues with newer versions.

Failing tests in the SQLA compliance test suite, in regard to the turbodbc dialect
won't be addressed until explicitly required/requested by users.

Note: It is also very likely that turbodbc support will be dropped in future versions.

## 🐞 Fixed

* Fixed invalid implicit autocommit behaviour, for details see [this issue](https://github.com/exasol/sqlalchemy-exasol/issues/335).

## ✨ Added

* Added websocket based dbapi2 compliant database driver

## 🔧 Changed

* Updated pytest
* Updated Dependencies
* Loosened version constraints on 'packaging' dependency
* Loosened dev dependency constraints

## 🧰 Internal
* Changed changelog workflow

    - Removed scriv
    - Added unreleased section to track unreleased changes

* Simplified workflows by factoring out python & poetry setup into an action
* Added a internal category to the changelog fragment template
* Added manual trigger for the gh-pages workflow
* Removed workaround for outdated DB versions
  (for further details see [here](https://github.com/exasol/sqlalchemy-exasol/issues/5))
* Added exasol-integration-test-docker-environment as dev dependency

