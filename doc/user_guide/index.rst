.. _user_guide:

:octicon:`person` User Guide
============================

.. toctree::
    :maxdepth: 2

    getting_started
    configuration/index


General Notes
~~~~~~~~~~~~~

- Schema name and parameters are optional for the host URL
- Always use all lower-case identifiers for schema, table and column names. SQLAlchemy treats all lower-case identifiers as case-insensitive, the dialect takes care of transforming the identifier into a case-insensitive representation of the specific database (in case of EXASol this is upper-case as for Oracle)
- As of Exasol client driver version 4.1.2 you can pass the flag `INTTYPESINRESULTSIFPOSSIBLE=y` in the connection string (or configure it in your DSN). This will convert DECIMAL data types to Integer-like data types. Creating integers takes on about 30% of the time compared to Decimals.

Known Issues
~~~~~~~~~~~~
* Insert
    - Insert multiple empty rows via prepared statements does not work in all cases
