.. _connection_specification:

Connection Specification
========================

For connecting to a database, SQLAlchemy requires to call ``create_engine()`` with an
argument specifying the detailed parameters of the connection. The parameters include:
the host and port of the database service, the username and password, and other options.

The connection may be of data type :ref:`str <url_string>` or :ref:`URL <instance_url>`. For data
type ``str``, the connection parameters will be parsed, and thus, special characters
must be properly escaped.

.. note::
    For more information, see the `SQLAlchemy documentation <https://docs.sqlalchemy.org/en/20/core/engines.html>`__.
    General parameters & specific parameters for the SQLAlchemy-Exasol dialect are given in :ref:`connection_parameters`.

.. _instance_url:

``URL``
^^^^^^^

.. literalinclude:: ../../../examples/configuration/connection_specification/0_instance_of_url.py
       :language: python3
       :caption: examples/configuration/connection_specification/0_instance_of_url.py

.. _url_string:

``str``
^^^^^^^

.. literalinclude:: ../../../examples/configuration/connection_specification/1_url_string.py
       :language: python3
       :caption: examples/configuration/connection_specification/1_url_string.py
