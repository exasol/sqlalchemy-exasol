# Unreleased

## Refactoring
- #610: Altered string input into `Connection.execute()` to be handled properly

## Internal

- #558: Updated to poetry 2.1.2 & relocked dependencies to resolve CVE-2025-27516
- #548: Replaced pytest-exasol-itde with pytest-backend
- Relocked dependencies to resolve CVE-2025-43859
- #564: Replaced nox test:unit with that from exasol-toolbox
- Reformatted files to meet project specifications
- #588: Updated to exasol-toolbox 1.6.0 and relocked dependencies to resolve CVE-2025-50182, CVE-2025-50181, & CVE-2024-47081
- #605: Removed non-ASCII unicode from templates & relocked dependencies to resolve CVE-2025-8869 (pip -> transitive dependency)