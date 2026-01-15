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

.. literalinclude:: ../../../examples/configuration/connection_specification/0_instance_of_url.py
       :language: python3
       :caption: examples/configuration/connection_specification/0_instance_of_url.py

.. _url_string:

URL string
^^^^^^^^^^

.. literalinclude:: ../../../examples/configuration/connection_specification/1_url_string.py
       :language: python3
       :caption: examples/configuration/connection_specification/1_url_string.py

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
