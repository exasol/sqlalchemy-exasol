.. _custom_fetch_mapper_example:

Custom Fetch Mapper
===================

This example compares values returned by PyExasol's default WebSocket fetch
mapper with values returned by a custom mapper. The custom mapper converts
``VARCHAR`` values to uppercase and leaves other values unchanged. It creates
and seeds the ``PYEXASOL_DBAPI_TYPE_CONVERSION`` table
when it is not already populated, then prints both rows side by side.

Configure the connection in ``examples/config.py`` or with the environment
variables documented by the :ref:`example_configuration` example.

Run it from the repository root with:

.. code-block:: bash

   poetry run python -m examples.configuration.fetch_mapper

.. literalinclude:: ../../../examples/configuration/fetch_mapper.py
   :language: python3
   :caption: examples/configuration/fetch_mapper.py
