.. _example_configuration:

Connection Configuration
------------------------

For running the examples, file ``examples/config.py`` provides a default connection configuration
for an Exasol Docker DB. If your setup differs, you can either modify the values in the
``CONNECTION_CONFIG`` initialization or override the default values by setting
exported environment variables, as specified in the docstring.

Environment variables may be set like:

.. code-block:: shell

    export EXA_USERNAME='abcd'
    export EXA_QUERY='{"FINGERPRINT": "abcde1234"}'


.. literalinclude:: ../../../examples/config.py
       :language: python3
       :caption: examples/config.py
