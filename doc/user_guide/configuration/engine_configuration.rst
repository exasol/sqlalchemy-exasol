Engine Configuration
=====================

Options for Specifying the URL
------------------------------

The value passed to ``create_engine()`` may be either an :ref:`instance_url`
or a :ref:`url_string`. For the :ref:`url_string`, the connection parameters will be
parsed, and thus, special characters must be properly escaped.

.. note::
    For more information, like which parameters are allowed into an :ref:`instance_url`
    and which characters need to be escaped for the :ref:`url_string`, see
    the `SQLAlchemy documentation <https://docs.sqlalchemy.org/en/20/core/engines.html>`__.

    Check out which parameters are suggested to include for certain scenarios in :ref:`suggested_parameters`.
    Specific parameters for the SQLAlchemy-Exasol dialect are given in :ref:`dialect_specific_params`.


.. _instance_url:

Instance of ``URL``
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from sqlalchemy import create_engine, URL

    url_object = URL.create(
        drivername="exa+websocket",
        username="sys",
        password="exasol",
        host="127.0.0.1",
        port="8563",
        query={"AUTOCOMMIT": "y"},
    )

    create_engine(url_object)

.. _url_string:

URL string
^^^^^^^^^^

.. code-block:: python

    from sqlalchemy import create_engine

    user = "sys"
    password = "exasol"
    host = "127.0.0.1"
    port = "8563"
    schema = "my_schema"
    # All parameters specified in the query are of form NAME=value
    # The first parameter in the query is preceded by a `?`.
    # Additional parameters are preceded by a `&`.
    query = "?AUTOCOMMIT=y"

    url_string = f"exa+websocket://{user}:{password}@{host}:{port}/{schema}{query}"

    create_engine(url_string)

.. _suggested_parameters:

Suggested Parameters
--------------------

In the table below are selected parameters that are suggested for specific scenarios.
The examples are given for :ref:`instance_url` where ``query`` is a keyword
argument supplied to the ``URL.create()`` constructor.

.. list-table::
   :header-rows: 1

   * - Name
     - Example
     - Description
   * - CONNECTIONLCALL
     - .. code-block:: python

         query={
          "CONNECTIONLCALL": "en_US.UTF-8"
         }
     - To avoid errors due to different code pages used by the client process (Python)
       and the Exasol driver, this is recommended to use, particular for Unix-based
       systems.

.. _dialect_specific_params:

Dialect-Specific Parameters
---------------------------
In the table below are additional parameters that are specific to the SQLAlchemy-Exasol
dialect. The examples are given for :ref:`instance_url` where ``query`` is a keyword
argument supplied to the ``URL.create()`` constructor.

.. list-table::
   :header-rows: 1

   * - Name
     - Example
     - Description
   * - AUTOCOMMIT
     - .. code-block:: python

         query={
          "AUTOCOMMIT": "y"
         }
     - This indicates if the connection should automatically perform commits or not.
       The parsed value is case insensitive:

        * To enable autocommit, specify ``"y"`` or ``"yes"``.
        * To disable autocommit, specify ``"n"`` or ``"no"``.

       The default is for autocommit to be enabled (``"y"``).
