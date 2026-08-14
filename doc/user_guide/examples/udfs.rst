Creating Exasol UDFs
====================

SQLAlchemy can be used to create and call Exasol UDFs (`User Defined Functions
<udfs_>`_) just as an ordinary SQL editor would allow to do:

.. literalinclude:: ../../../test/integration/exasol/test_udf.py
  :language: python
  :start-at: UDF =
  :dedent: 8

.. _udfs: https://docs.exasol.com/db/latest/database_concepts/udf_scripts.htm
