.. _engine_configuration:

Engine Configuration
=====================

.. _specifying_url:

Options for Specifying the URL
------------------------------

The value passed to ``create_engine()`` may be either an :ref:`instance_url`
or a :ref:`url_string`. For the ``url_string``, the connection parameters will be
parsed, and thus, special characters must be properly escaped.

.. note::
    For more information, like which parameters are allowed into an ``instance_url``
    and which characters need to be escaped for the ``url_string``, see
    the `SQLAlchemy documentation <https://docs.sqlalchemy.org/en/20/core/engines.html>`__.

    Check out which parameters are suggested to include for certain scenarios in :ref:`suggested_parameters`.
    Specific parameters for the SQLAlchemy-Exasol dialect are given in :ref:`dialect_specific_params`.


.. _instance_url:

Instance of ``URL``
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from sqlalchemy import create_engine, URL

    # All parameters, which are not keyword arguments for `URL.create`,
    # should be specified in the `query` dictionary.
    # For two specified parameters, this would follow this pattern:
    #   query = {"<Keyword>": "<value>", "<Keyword2>": "<value2>"}
    query={
        "AUTOCOMMIT": "y",
        "CONNECTIONLCALL": "en_US.UTF-8"
    }

    url_object = URL.create(
        drivername="exa+websocket",
        username="sys",
        password="exasol",
        host="127.0.0.1",
        port=8563,
        query=query,
    )

    create_engine(url_object)

.. _url_string:

URL string
^^^^^^^^^^

.. code-block:: python

    from sqlalchemy import create_engine

    username = "sys"
    password = "exasol"
    host = "127.0.0.1"
    port = "8563"
    schema = "my_schema"
    # All parameters, which are not keyword arguments for `URL.create`,
    # should be specified in `query` and are of the form NAME=value
    # The first parameter in the query is preceded by a `?`.
    # Additional parameters are preceded by a `&`.
    # For example, two parameters would follow this pattern:
    #    query = "?<Keyword>=<value>&<Keyword2>=<value2>"
    query = "?AUTOCOMMIT=y&CONNECTIONLCALL=en_US.UTF-8"

    url_string = f"exa+websocket://{username}:{password}@{host}:{port}/{schema}{query}"

    create_engine(url_string)

.. _suggested_parameters:

Suggested Parameters
--------------------

The table below suggests selected parameters for specific scenarios and gives the values
as needed for the :ref:`instance_url`. One or more specified parameters may be passed to
the connection URL as described in :ref:`specifying_url`.

.. list-table::
   :header-rows: 1

   * - Keyword
     - Description
   * - CONNECTIONLCALL
     - To avoid errors due to different code pages used by the client process (Python)
       and the Exasol driver, it is recommend to use ``"en_US.UTF-8"``, particularly for
       Unix-based systems.

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
