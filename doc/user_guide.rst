.. _user_guide:

:octicon:`person` User Guide
============================

SQLAlchemy-Exasol is a dialect extension for SQLAlchemy, implementing support for Exasol databases.

.. note::
    For more details on SQLAlchemy, please consult its `documentation <https://docs.sqlalchemy.org/en/14/>`_.

Getting Started
~~~~~~~~~~~~~~~

#. Install the `SQLAlchemy-Exasol extension <https://pypi.org/project/sqlalchemy_exasol/>`_

    .. code-block:: shell

        $ pip install sqlalchemy-exasol

    .. note::

        SQLAlchemy will be installed as well, as it is a required dependency for SQLAlchemy-Exasol.

#. Execute queries

    .. code-block:: python

        from sqlalchemy import create_engine, sql

        user = "sys"
        password = "exasol"
        host = "127.0.0.1"
        port = "8563
        schema = "my_schema"

        # At least on Unix systems you can pass URL parameter
        # `CONNECTIONLCALL=en_US.UTF-8` to avoid errors
        # due to different code pages used by the client process (Python)
        # and the EXASOL driver.
        url = f"exa+websocket://{user}:{password}@{host}:{port}/{schema}?CONNECTIONLCALL=en_US.UTF-8"
        engine = create_engine(url)

        # engine.connect() is for non-DML or non-DDL queries
        with engine.connect() as con:
            # A query given as a string should, for future compatibility with
            # sqlalchemy 2.x, be passed through `sqlalchemy.sql.text`.
            result = con.execute(sql.text("select 42 from dual")).fetchall()

        # engine.begin() is for DML & DDL, as we don't want to rely on autocommit
        # but you can with `engine.connect()` commit as you go with `con.commit()`
        with engine.begin() as con:
        ...


Further Examples
~~~~~~~~~~~~~~~~

.. code-block:: python

    from sqlalchemy import create_engine, sql

    user = "sys"
    password = "exasol"
    host = "127.0.0.1"
    port = "8563
    schema = "my_schema"

    url = f"exa+websocket://{user}:{password}@{host}:{port}/{schema}?CONNECTIONLCALL=en_US.UTF-8"
    engine = create_engine(url)
    query = "select 42 from dual"
    with engine.connect() as con:
        result = con.execute(sql.text(query)).fetchall()


.. code-block:: python

    from sqlalchemy import create_engine

    """
    ATTENTION:
    In terms of security it is NEVER a good idea to disable certificate validation!
    In rare cases, it may be handy for non-security related reasons.
    That said, if you are not 100% sure about your scenario, stick with the secure defaults.
    In most cases, having a valid fingerprint, certificate and/or configuring the truststore(s)
    appropriately is the best/correct solution.
    """
    user = "sys"
    password = "exasol"
    host = "127.0.0.1"
    port = "8563

    # To disable certificate validation -> NOT recommended
    ssl_certificate = "SSL_VERIFY_NONE"
    engine = create_engine(f"exa+websocket://{user}:{password}@{host}:{port}?CONNECTIONLCALL=en_US.UTF-8&SSLCertificate={ssl_certificate}")
    with engine.connect() as con:
        ...

    # To validate via fingerprint
    fingerprint = "C70EB4DC0F62A3BF8FD7FF22D2EB2C489834958212AC12C867459AB86BE3A028"
    url = f"exa+websocket://{user}:{password}@{host}:{port}?CONNECTIONLCALL=en_US.UTF-8&FINGERPRINT={fingerprint}"
    engine = create_engine(url)
    with engine.connect() as con:
        ...


General Notes
~~~~~~~~~~~~~

- Schema name and parameters are optional for the host URL
- At least on Unix systems you can pass URL parameter `CONNECTIONLCALL=en_US.UTF-8` to avoid errors due to different code pages used by the client process (Python) and the EXASOL driver.
- Always use all lower-case identifiers for schema, table and column names. SQLAlchemy treats all lower-case identifiers as case-insensitive, the dialect takes care of transforming the identifier into a case-insensitive representation of the specific database (in case of EXASol this is upper-case as for Oracle)
- As of Exasol client driver version 4.1.2 you can pass the flag `INTTYPESINRESULTSIFPOSSIBLE=y` in the connection string (or configure it in your DSN). This will convert DECIMAL data types to Integer-like data types. Creating integers takes on about 30% of the time compared to Decimals.

Known Issues
~~~~~~~~~~~~
* Insert
    - Insert multiple empty rows via prepared statements does not work in all cases
