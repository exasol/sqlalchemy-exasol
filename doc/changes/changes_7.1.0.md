# 7.1.0 - 2026-06-09

## Summary

In this minor release, we add access to table comments via `get_table_comment` and column comments via `get_columns`.

## Feature

* #753: Added access to table and column comments

## Refactoring

* #738: Replaced `version.py` usage with method based on `pyproject.toml`
* #743: Updated to `exasol-toolbox` version 8.0.0
* #747: Added `export` plugin to `pyproject.toml` for `exasol-toolbox` usage
* #750: Updated to `exasol-toolbox` version 8.1.1

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability       | Affected | Fixed in |
|------------|---------------------|----------|----------|
| gitpython  | GHSA-mv93-w799-cj2w | 3.1.49   | 3.1.50   |
| idna       | CVE-2026-45409      | 3.11     | 3.15     |
| pip        | PYSEC-2026-196      | 26.1     | 26.1.2   |
| pytest     | CVE-2025-71176      | 8.4.2    | 9.0.3    |
| urllib3    | PYSEC-2026-142      | 2.6.3    | 2.7.0    |
| urllib3    | PYSEC-2026-141      | 2.6.3    | 2.7.0    |

* #741: Resolved vulnerabilities by relocking `poetry.lock` and increased allowed `pytest` and `exasol-integration-test-docker-environment`
* #749: Resolved vulnerabilities by relocking `poetry.lock`

## Dependency Updates

### `main`

* Updated dependency `pyexasol:2.0.0` to `2.2.1`

### `dev`

* Updated dependency `exasol-integration-test-docker-environment:5.0.0` to `6.2.0`
* Updated dependency `exasol-toolbox:7.0.0` to `8.1.1`
* Updated dependency `nox:2025.11.12` to `2026.4.10`
* Updated dependency `pydantic:2.12.5` to `2.13.4`
* Updated dependency `pydantic-settings:2.12.0` to `2.14.1`
* Updated dependency `pytest:8.4.2` to `9.0.3`
* Updated dependency `pytest-exasol-backend:1.4.0` to `1.4.1`
