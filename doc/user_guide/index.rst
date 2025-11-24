.. _user_guide:

:octicon:`person` User Guide
============================

.. toctree::
    :maxdepth: 2

    getting_started
    configuration/index

Getting Started
~~~~~~~~~~~~~~~

#. Execute queries

.. code-block:: python

        from sqlalchemy import create_engine, sql

        user = "sys"
        password = "exasol"
        host = "127.0.0.1"
        port = "8563
        schema = "my_schema"

        url = f"exa+websocket://{user}:{password}@{host}:{port}/{schema}?CONNECTIONLCALL=en_US.UTF-8"
        engine = create_engine(url)

        # engine.connect() is for non-DML or non-DDL queries
        with engine.connect() as con:
            # A query given as a string should, for future compatibility with
            # sqlalchemy 2.x, be passed through `sqlalchemy.sql.text`.
            result = con.execute(sql.text("select 42 from dual")).fetchall()

        # For easier usage of transactions, you can use engine.begin() for DML & DDL,
        # if you don't want to rely on autocommit. However, you can with
        # `engine.connect()` commit as you go with `con.commit()` or use, for more
        # complex scenarios:
        #   with engine.connect() as con:
        #      with conn.begin():
        #        ...
        with engine.begin() as con:
        ...


General Notes
~~~~~~~~~~~~~

- Schema name and parameters are optional for the host URL
- Always use all lower-case identifiers for schema, table and column names. SQLAlchemy treats all lower-case identifiers as case-insensitive, the dialect takes care of transforming the identifier into a case-insensitive representation of the specific database (in case of EXASol this is upper-case as for Oracle)
- As of Exasol client driver version 4.1.2 you can pass the flag `INTTYPESINRESULTSIFPOSSIBLE=y` in the connection string (or configure it in your DSN). This will convert DECIMAL data types to Integer-like data types. Creating integers takes on about 30% of the time compared to Decimals.

Known Issues
~~~~~~~~~~~~
* Insert
    - Insert multiple empty rows via prepared statements does not work in all cases
