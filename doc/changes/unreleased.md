# Unreleased

## Summary

This major release adds support for DLT and also improves the exceptions to be
PEP-249 compliant.

## Features

* #671: Added DLT support
    * Adds an exception handler for PyExasol errors bubbling up and converts them to proper PEP-249 exceptions.
    * Maps sqlalchemy `DATETIME` type to Exasol `TIMESTAMP`.
    * Formats datetime so it works within DLT.
    * Binary types such as `UUINT`, `BLOB`, `BINARY` and `VARBINARY` now throw a clear error when used.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency    | Vulnerability  | Affected | Fixed in |
|---------------|----------------|----------|----------|
| black         | CVE-2026-32274 | 25.12.0  | 26.3.1   |
| cryptography  | CVE-2026-34073 | 46.0.5   | 46.0.6   |
| cryptography  | CVE-2026-39892 | 46.0.5   | 46.0.7   |
| requests      | CVE-2026-25645 | 2.32.5   | 2.33.0   |
| pygments      | CVE-2026-4539  | 2.19.2   | 2.20.0   |
| python-dotenv | CVE-2026-28684 | 1.2.1    | 1.2.2    |

* #733: Fixed vulnerabilities by re-locking transitive dependencies
* #736: Fixed vulnerabilities by re-locking transitive dependencies & updated to exasol-toolbox `7.0.0`
