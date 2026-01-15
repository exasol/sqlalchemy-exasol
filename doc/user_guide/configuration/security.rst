.. _security:

Security
========

SQLAlchemy-Exasol is a dialect extension for SQLAlchemy, which utilizes
`PyExasol <https://github.com/exasol/pyexasol/>`__ in the backend.
It works with different Exasol database variants: on-premise and, for
testing purposes, Docker-based. Each of these have shared and unique
authentication methods and require a TLS/SSL certificate setup. Throughout this
guide on security, an overview of the security features of SQLAlchemy-Exasol is
provided.

.. _authentication:

Authentication
**************

For the various Exasol DBs, there are different ways to set up and use the access
credentials for a connection made with the :ref:`instance_url` or :ref:`url_string`
provided to the engine.

+------------------+------------------------------+----------------------------------------+
| Exasol DB        | Setting Credentials          | Parameters                             |
+==================+==============================+========================================+
| on-premise       | `on-premise authentication`_ | * ``username``                         |
|                  |                              | * ``password``                         |
+------------------+------------------------------+----------------------------------------+
| SaaS             | `SAAS authentication`_       | * ``username``                         |
|                  |                              | * ``password``                         |
+------------------+------------------------------+----------------------------------------+
| Docker (testing) | `Docker authentication`_     | * ``username``                         |
|                  |                              | * ``password``                         |
+------------------+------------------------------+----------------------------------------+

.. note::
    While PyExasol supports connecting with SaaS database instances using
    ``access_token`` or ``refresh_token``, the SQLAlchemy-Exasol dialect does not yet
    support these.

.. _on-premise authentication: https://docs.exasol.com/db/latest/sql/create_user.htm
.. _SAAS authentication: https://docs.exasol.com/saas/administration/access_mngt/access_management.htm#Databaseaccessmanagement
.. _Docker authentication: https://github.com/exasol/docker-db?tab=readme-ov-file#connecting-to-the-database

.. _tls:

Transport Layer Security (TLS)
******************************

Similar to other Exasol connectors, SQLAlchemy-Exasol supports using the cryptographic
protocol TLS. As a part of the TLS handshake, the drivers require the SSL/TLS certificate
used by Exasol to be verified. This is a standard practice to increase the security of
connections by preventing man-in-the-middle attacks.

Please check out Exasol's user-friendly tutorials on TLS:

* `An introduction to TLS <https://github.com/exasol/tutorials/blob/1.0.0/tls/doc/tls_introduction.md>`__
* `TLS with Exasol <https://github.com/exasol/tutorials/blob/1.0.0/tls/doc/tls_with_exasol.md>`__
* `TLS in UDFs <https://github.com/exasol/tutorials/blob/1.0.0/tls/doc/tls_in_udfs.md>`__

Additionally, Exasol provides the following technical articles relating to TLS:

- `Database connection encryption at Exasol <https://exasol.my.site.com/s/article/Database-connection-encryption-at-Exasol/>`__
- `CHANGELOG: TLS for all Exasol drivers <https://exasol.my.site.com/s/article/Changelog-content-6507>`__
- `CHANGELOG: Database accepts only TLS connections <https://exasol.my.site.com/s/article/Changelog-content-16927>`__
- `Generating TLS files yourself to avoid providing a fingerprint <https://exasol.my.site.com/s/article/Generating-TLS-files-yourself-to-avoid-providing-a-fingerprint/>`__
- `TLS connection fails <https://exasol.my.site.com/s/article/TLS-connection-fails>`__

.. _certificate_verification:

About Certificate Verification
------------------------------
Certificates verification provides proof of the authenticity of the database you are connecting to.

As further discussed in
`Certificate and Certificate Agencies <https://github.com/exasol/tutorials/blob/1.0.0/tls/doc/tls_introduction.md#certificates-and-certification-agencies>`__,
there are three kinds of certificates:

* ones from a public Certificate Authority (CA)
* ones from a private CA
* ones that are self-signed

Before using a certificate for certificate verification, your IT Admin should ensure that
whatever certificate your Exasol instance uses, is the most secure:

- Exasol running on-premise uses a default self-signed SSL certificate. Your IT Admin
  should replace the certificate with one provided by your organization. For further
  context and instructions, see:
  - `Conceptual: Incoming TLS Connections <https://github.com/exasol/tutorials/blob/1.0.0/tls/doc/tls_with_exasol.md#incoming-tls-connections>`__
  - `TLS Certificate Instructions <https://docs.exasol.com/db/latest/administration/on-premise/access_management/tls_certificate.htm>`__.
  - `confd_client cert_update <https://docs.exasol.com/db/latest/confd/jobs/cert_update.htm>`_
- Exasol Docker uses a self-signed SSL certificate by default. You, as a user, may
  generate a proper SSL certificate and submit it for use via the ConfD API. More
  details are available on:

   - `GitHub for Exasol Docker <https://github.com/exasol/docker-db>`_
   - `ConfD API <https://docs.exasol.com/db/latest/confd/confd.htm>`_
   - `confd_client cert_update <https://docs.exasol.com/db/latest/confd/jobs/cert_update.htm>`_

.. note::

    For setting up a certificate, see the information provided in
    `PyExasol's security documentation <https://exasol.github.io/pyexasol/master/user_guide/configuration/security.html#setup>`__.

.. _fingerprint_verification:

Fingerprint Verification
------------------------

Similar to JDBC / ODBC drivers, SQLAlchemy-Exasol supports fingerprint verification.
For more information, see the ODBC entry on `fingerprint <https://docs.exasol.com/db/latest/connect_exasol/drivers/odbc/using_odbc.htm?Highlight=prepared%20statement#fingerprint>`__.

.. code-block:: python

    from sqlalchemy import create_engine, URL

    fingerprint = "0ACD07D4E9CEEB122773A71B9C3BD01CE49FC99901DE7C0E0030C942805BA64C"

    url_object = URL.create(
        drivername="exa+websocket",
        username="sys",
        password="exasol",
        host="127.0.0.1",
        port=8563,
        query={"FINGERPRINT": fingerprint},
    )

    create_engine(url_object)

Additionally, you can **disable the certificate check completely** by setting "nocertcheck" (case-insensitive) as a fingerprint value.

.. warning::
    However, this should **NEVER** be used for production.

.. code-block:: python

    from sqlalchemy import create_engine, URL

    url_object = URL.create(
        drivername="exa+websocket",
        username="sys",
        password="exasol",
        host="127.0.0.1",
        port=8563,
        query={"FINGERPRINT": "nocertcheck"},
    )

    create_engine(url_object)




Custom Certificate Location
---------------------------

At this time, it is not possible to specify a custom certificate location into the
connection URL. This is supported by the backend code (PyExasol) and is a feature that
could be added to SQLAlchemy-Exasol.

.. _disable_certificate_verification:

Disable Certificate Verification
----------------------------------

As discussed in the :ref:`dialect_specific_params`, SQLAlchemy-Exasol by default has certificate
verification turned on. This is to improve security and prevent man-in-the-middle
attacks. In the case of testing with a local database, a user might want to temporarily
disable certificate verification.

.. warning::
    Due to the increased security risks, this change should :octicon:`alert` **NEVER** be used for production.

    For more context regarding the security risks,
    see `An introduction to TLS <https://github.com/exasol/tutorials/blob/1.0.0/tls/doc/tls_introduction.md>`__.

.. code-block:: python

  from sqlalchemy import create_engine, URL

    url_object = URL.create(
        drivername="exa+websocket",
        username="sys",
        password="exasol",
        host="127.0.0.1",
        port=8563,
        query={"SSLCertificate": "SSL_VERIFY_NONE"},
    )

    create_engine(url_object)

Alternatively, you can disable the certificate check by setting "nocertcheck" as the fingerprint value, see :ref:`fingerprint_verification` above.
