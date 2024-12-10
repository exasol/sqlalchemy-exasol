# 2.0.6 — 2019-08-12

## 🗑️ Removed

- Removed deprecated setting of 'convert_unicode' on engine

## ✨ Added

- Added support for empty set expressions required by new SQLA tests

## 🔧 Changed

- Updated PyODBC dependency to 4.0.27
- Updated SQLAlchemy dependency to 1.3.6

## 🐞 Fixed

- Fixed bug in reflection of CHAR colums (missing length). Contribution from @vamega
- Fixed bug in rendering of SQL statements with common table expressions (CTE). Contribution from @vamega


