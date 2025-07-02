# 4.0.0 — 2022-12-01

## ✨ Added

* Added support for SQLA 1.4

    **🚨 Attention:**

    This upgrade is not backwards compatible with SQLA < 1.4

    This version may impact the performance (see also [SQLAlchemy docs](https://docs.sqlalchemy.org/en/14/faq/performance.html#why-is-my-application-slow-after-upgrading-to-1-4-and-or-2-x)).
    If you are not willing or able to pay those potential performance hits, you should wait until the [tracking-issue #190](https://github.com/exasol/sqlalchemy-exasol/issues/190) is resolved.


## 🗑️ Removed

* Removed custom merge statement

  (If we will be notified, that someone depends on this feature, we are open to add it again.)

## 🔐 Security

- Evaluated CVE-2022-42969
     - CVE will be silenced
     - The affected code is not used by our project itself,
       nor by the dependencies pulling in the vulnerable library.

        Checked dependencies:

        * Nox (Code search)
        * Pytest (Code search + [tracking-issue #10392](https://github.com/pytest-dev/pytest/issues/10392))

## 🔧 Changed

- Updated all dependencies

## 🐞 Fixed

- Fixed link to project documentation

