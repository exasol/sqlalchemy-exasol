.. _security:

Security
========

SQLAlchemy-Exasol is a dialect extension for SQLAlchemy, which utilizes
`PyExasol <https://github.com/exasol/pyexasol/>`__ in the backend.
It works with different Exasol database variants: on-premise and, for
testing purposes, Docker-based. Each of these have shared and unique
authentication methods and require a TLS/SSL certificate setup. Throughout this
guide on security, an overview of the security features of SQLAlchemy-Exasol is
provided, as well as examples and links to the relevant PyExasol documentation.
