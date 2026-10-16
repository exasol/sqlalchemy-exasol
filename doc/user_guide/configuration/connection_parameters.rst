.. _connection_parameters:

Connection Parameters
=====================

Connection Parameter Locations
------------------------------

SQLAlchemy-Exasol connection settings are supplied in one of three places:

* Connection URL fields such as ``drivername``, ``username``, ``password``,
  ``host``, and ``port`` are specified in the URL passed to ``create_engine``.
* SQLAlchemy-Exasol URL query parameters are supplied as string values in the
  URL's ``query`` dictionary or query string.
* DBAPI options that require Python values, such as ``fetch_mapper``, are
  supplied in SQLAlchemy's ``connect_args`` dictionary.

.. _sqlalchemy_parameters:

General SQLAlchemy Parameters
-----------------------------

The table below lists parameters used in the :ref:`connection_specification`.

.. list-table::
   :header-rows: 1

   * - Parameter
     - Description
   * - drivername
     - The name of the database backend.
       For SQLAlchemy-Exasol, this is ``"exa+websocket"``.
   * - username
     - The name of the user for authentication, e.g. ``"sys"``.
   * - password
     - The password associated with the given username. This should not be encoded,
       and special characters do not need to be escaped, e.g. ``"exasol"``.
   * - host
     - The host data source name (DSN) to access the database, e.g. ``"127.0.0.1"``.
   * - port
     - The port number to access the database, e.g. ``8563``.
   * - query
     - A dictionary of string keys to string values to be passed
       to the dialect upon connecting, e.g. ``{"AUTOCOMMIT": "y"}``.
       For other relevant keywords, see :ref:`dialect_specific_params`.



.. _dialect_specific_params:

Specific URL Query Parameters for SQLAlchemy-Exasol
----------------------------------------------------
The table below lists URL query parameters supported by the SQLAlchemy-Exasol
dialect. Add them to the URL query string or the ``query`` dictionary passed to
``URL.create``; their values are supplied as strings and converted by the
dialect as needed.

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
          (e.g. ``"0ACD07D4E9CEEB122773A71B9C3BD01CE49FC99901DE7C0E0030C942805BA64C"``).

       For more information about fingerprint verification, please see
       :ref:`fingerprint_verification`.
   * - SSLCertificate
     - This indicates if the connection should verify the SSL certificate or not.

        * (default) SSL certificate verification is active. There is currently not an
          option for users to directly specify this as enabled.
        * To disable SSL certificate verification (**NOT** recommended and **NOT** secure),
          specify ``"SSL_VERIFY_NONE"``. This value is case-insensitive.

       For more information about verifying the SSL certificate, please see
       :ref:`certificate_verification`.


DBAPI Connection Arguments
--------------------------

Some PyExasol DBAPI options are Python values rather than URL-compatible
strings. Pass these through SQLAlchemy's ``connect_args`` dictionary in
``create_engine`` instead of putting them in the connection URL.

.. list-table::
   :header-rows: 1

   * - Argument
     - Description
   * - ``fetch_mapper``
     - Available with PyExasol 3.0.0 and newer. A callable
       ``fetch_mapper(value, data_type)`` is used to convert values returned by
       the WebSocket DBAPI. See the
       :ref:`custom fetch mapper example <custom_fetch_mapper_example>`.


.. _pyexasol_compatibility:

PyExasol Compatibility and Value Conversion
--------------------------------------------

SQLAlchemy-Exasol uses the WebSocket DBAPI provided by
`PyExasol <https://exasol.github.io/pyexasol/master/user_guide/exploring_features/advanced_topics/dbapi.html>`__.
PyExasol 3.0.0 changed the default WebSocket DBAPI conversion so that values are converted to
Python types as early as possible, in accordance with PEP 249.

The following table describes values exposed by SQLAlchemy-Exasol through the
WebSocket DBAPI. ``None`` is returned for ``NULL`` values for all types.

.. list-table::
   :header-rows: 1

   * - Exasol type
     - PyExasol < 3.0.0
     - PyExasol >= 3.0.0
   * - ``BOOLEAN``
     - ``bool``
     - ``bool``
   * - ``CHAR``
     - ``str``
     - ``str``
   * - ``DATE``
     - ``datetime.date``
     - ``datetime.date``
   * - ``DECIMAL(p, 0)``
     - ``decimal.Decimal``
     - ``decimal.Decimal``
   * - ``DECIMAL(p, s)`` where ``s > 0``
     - ``decimal.Decimal``
     - ``decimal.Decimal``
   * - ``DOUBLE``
     - ``float``
     - ``float``
   * - ``GEOMETRY``
     - ``str``
     - ``str``
   * - ``HASHTYPE``
     - metadata ``KeyError``
     - ``str``
   * - ``INTERVAL DAY TO SECOND``
     - ``str``
     - ``ExaTimeDelta``
   * - ``INTERVAL YEAR TO MONTH``
     - ``str``
     - ``str``
   * - ``TIMESTAMP``
     - ``datetime.datetime``
     - ``datetime.datetime``
   * - ``TIMESTAMP WITH LOCAL TIME ZONE``
     - ``str``
     - ``str``
   * - ``VARCHAR``
     - ``str``
     - ``str``

For release-specific conversion details and the complete list of changes, see the
`PyExasol 3.0.0 release notes <https://github.com/exasol/pyexasol/releases/tag/3.0.0>`__.


Custom fetch mapper
~~~~~~~~~~~~~~~~~~~

Applications can provide their own PyExasol ``fetch_mapper`` through
SQLAlchemy's ``connect_args``. The mapper receives ``(value, data_type)`` for
each fetched value, as described in PyExasol's
`DBAPI documentation <https://exasol.github.io/pyexasol/master/user_guide/exploring_features/advanced_topics/dbapi.html>`__.
It replaces PyExasol's default mapper, so applications must handle the value
types they need. See the :ref:`custom fetch mapper example
<custom_fetch_mapper_example>`.
