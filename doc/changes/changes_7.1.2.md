# 7.1.2 - 2026-08-04

## Summary

This patch release lifts the Python 3.14 downpin, as the affected dependencies have
been updated.


## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency        | Vulnerability       | Affected | Fixed in |
|-------------------|---------------------|----------|----------|
| cryptography      | GHSA-537c-gmf6-5ccf | 48.0.0   | 48.0.1   |
| cryptography      | CVE-2026-69248      | 48.0.0   | 49.0.0   |
| cryptography      | CVE-2026-69249      | 48.0.0   | 49.0.0   |
| gitpython         | GHSA-2f96-g7mh-g2hx | 3.1.50   | 3.1.51   |
| gitpython         | GHSA-v396-v7q4-x2qj | 3.1.50   | 3.1.51   |
| gitpython         | GHSA-956x-8gvw-wg5v | 3.1.50   | 3.1.51   |
| gitpython         | GHSA-3rp5-jjmw-4wv2 | 3.1.50   | 3.1.53   |
| gitpython         | GHSA-fjr4-x663-mwxc | 3.1.50   | 3.1.54   |
| gitpython         | GHSA-6p8h-3wgx-97gf | 3.1.50   | 3.1.54   |
| gitpython         | GHSA-r9mr-m37c-5fr3 | 3.1.50   | 3.1.54   |
| gitpython         | GHSA-94p4-4cq8-9g67 | 3.1.50   | 3.1.55   |
| gitpython         | GHSA-3f7w-8rr8-f37f | 3.1.50   | 3.1.57   |
| gitpython         | GHSA-p538-c434-8v24 | 3.1.50   | 3.1.56   |
| msgpack           | GHSA-6v7p-g79w-8964 | 1.1.2    | 1.2.1    |
| pydantic-settings | GHSA-4xgf-cpjx-pc3j | 2.14.1   | 2.14.2   |

## Refactoring

* #763: Updated to `exasol-toolbox` 10.0.0
* #775: Updated to `exasol-toolbox` 10.4.0 and `poetry.lock`
* #672: Re-instated testing with Python 3.14

## Dependency Updates

### `main`

* Updated dependency `packaging:25.0` to `26.2`
* Updated dependency `pyexasol:2.2.1` to `2.3.0`
* Updated dependency `sqlalchemy:2.0.50` to `2.0.51`

### `dev`

* Updated dependency `exasol-integration-test-docker-environment:6.2.0` to `6.4.1`
* Updated dependency `exasol-toolbox:8.1.1` to `10.4.0`
* Updated dependency `nox:2026.4.10` to `2026.7.11`
* Updated dependency `pydantic-settings:2.14.1` to `2.14.2`
* Updated dependency `pytest-exasol-backend:1.4.1` to `1.5.1`
