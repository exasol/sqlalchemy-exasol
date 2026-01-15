.. _connection_parameters:

Connection Parameters
=====================

.. _sqlalchemy_parameters:

SQLAlchemy Parameters
---------------------



.. _dialect_specific_params:

Dialect-Specific Parameters
---------------------------
The table below lists additional parameters that are specific to the SQLAlchemy-Exasol
dialect and gives the values as needed for the :ref:`instance_url`. One or more
specified parameters may be passed to the connection URL as described in :ref:`specifying_url`.

.. list-table::
   :header-rows: 1

   * - Keyword
     - Description
   * - AUTOCOMMIT
     - This indicates if the connection automatically commits or not.
       The parsed value is case-insensitive.

        * (default) To enable autocommit, specify ``"y"`` or ``"yes"``.
        * To disable autocommit, specify ``"n"`` or ``"no"``.

   * - ENCRYPTION
     - This indicates if the connection should be encrypted or not.
       The parsed value is case-insensitive.

        * (default) To enable TLS encryption, specify ``"y"`` or ``"yes"``.
        * To disable TLS encryption (not recommended), specify ``"n"`` or ``"no"``.

       For more information about TLS encryption, please see :ref:`tls`.
   * - FINGERPRINT
     - An alternate to SSL certificate verification is to verify the connection
       via a fingerprint.

        * (default) Fingerprint verification is not active.
        * To use fingerprint verification, provide your fingerprint value
          (i.e. ``"0ACD07D4E9CEEB122773A71B9C3BD01CE49FC99901DE7C0E0030C942805BA64C"``).

       For more information about fingerprint verification, please see
       :ref:`fingerprint_verification`.
   * - SSLCertificate
     - This indicates if the connection should verify the SSL certificate or not.

        * The default behavior is to require SSL certificate verification. There
          is currently not an option to specify this further as enabled.
        * To disable SSL certificate verification (not recommended and not secure),
          specify ``"SSL_VERIFY_NONE"``. This value is case-insensitive.

       For more information about verifying the SSL certificate, please see
       :ref:`disable_certificate_verification`.
