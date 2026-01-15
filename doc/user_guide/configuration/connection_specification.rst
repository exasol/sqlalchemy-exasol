.. _connection_specification:

Connection Specification
========================

The connection may be specified as either an :ref:`instance_url` or a :ref:`url_string`.
When the connection is defined as a URL string, the connection parameters will be
parsed, and thus, special characters must be properly escaped.

.. note::
    For more information, see the `SQLAlchemy documentation <https://docs.sqlalchemy.org/en/20/core/engines.html>`__.

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
^^^^^^^^^^^^^^^^^^^^

The table below suggests selected parameters for specific scenarios and gives the values
as needed for the :ref:`instance_url`.

.. list-table::
   :header-rows: 1

   * - Keyword
     - Description
   * - CONNECTIONLCALL
     - To avoid errors due to different code pages used by the client process (Python)
       and the Exasol driver, it is recommend to use ``"en_US.UTF-8"``, particularly for
       Unix-based systems.
