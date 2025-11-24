Integration Test
================

The integration tests are located within `test/integration`. They are split in
two groups.

#. The SQLAlchemy conformance test suite

    The sqlalchemy conformance test suite is provided and maintained by the sqlalchemy project and intended to support third party dialect developers.
    For further details see also `README.dialects.rst <https://docs.exasol.com/db/latest/sql_reference.htm>`_.

#. Our custom Exasol test suite

    The Exasol test suite consists of test written and maintained by exasol.

.. note::

    In order to reduce the likelihood of test side effects, the `sqlalchemy` and the `exasol` test suites
    are executed in separate pytest test runs.

.. attention::

    The exasol database does do implicit schema/context changes (open & close schema)
    in certain scenarios. Keep this in mind when setting up (writing) tests.

    #. CREATE SCHEMA implicitly changes the CURRENT_SCHEMA context

        When you create a new schema, you implicitly open this new schema.

    #. DROP SCHEMA sometimes switches the context to <null>

        If the CURRENT_SCHEMA is dropped an implicit context switch to <null> is done

    For further details have a look at the `Exasol-Documentation <https://docs.exasol.com/db/latest/sql_reference.htm>`_.

    .. note::

        Creating/Using a new un-pooled connection can be used for protecting against
        this side effect.
