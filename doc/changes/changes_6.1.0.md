# 6.1.0 - 2026-02-06

## Summary

In this minor release, we have greatly added on to the
[User Guide](https://exasol.github.io/sqlalchemy-exasol/master/user_guide/index.html)
for SQLAlchemy-Exasol:

* For getting started, check out the remastered **Getting Started** page.
* Our **Configuration** pages have been edited to be crisper and provide more information
on forming your connection string and adhering to the best security practices.
* We have added a **Features** page, which gives an overview of benefits of using it.
Many of these entries contain links to our new **Examples** section and relevant
SQLAlchemy documentation.
* All of our code **Examples** are executed in the CI, so these should stay up-to-date
as future work on SQLAlchemy-Exasol continues.

Additionally, the `py.typed` file has been added, so type hints can propagate.


## Feature

* #693: Added `py.typed` file so type hints can propagate and added CI setup to execute examples

## Refactoring

* #681: Updated to `exasol-toolbox` 4.0.0
* #687: Re-locked the `poetry.lock` for vulnerabilities in the transitive dependencies: filelock, pynacl
* #690: Re-locked the `poetry.lock` for vulnerabilities in the transitive dependency: urllib3
* #710: Updated to `exasol-toolbox` 5.0.0
* #721: Updated to `exasol-toolbox` 5.1.0

## Documentation

* #698: Updated Configuration pages
* #703: Added ORM examples
* #706: Added more single and multiple entry ORM examples
* #712: Added to features information on: autoincremented columns, foreign keys, & automatic indexes
* #714: Added to features information on: caching + more non-ORM examples
* #716: Added to features information on: autocommit
* #718: Added to features information on: object name handling and query method chaining

## Dependency Updates

### `main`
* Updated dependency `pyexasol:1.3.0` to `2.0.0`

### `dev`
* Updated dependency `exasol-toolbox:3.0.0` to `5.1.0`
* Added dependency `pydantic:2.12.5`
* Added dependency `pydantic-settings:2.12.0`
* Updated dependency `pytest:7.4.4` to `8.4.2`
* Updated dependency `pytest-exasol-backend:1.2.3` to `1.2.4`
* Removed dependency `rich:13.9.4`
