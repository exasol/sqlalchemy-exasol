.. _example_orm_insert_multiple_entries:

Inserting Multiple Entries
==========================

This script inserts multiple entries into our two tables in one session & relies
on in-session auto-incrementing behavior. As mentioned in the :ref:`known_limitations`,
SQLAlchemy is slower than other drivers at performing multiple entry inserts.

This example is provided to show how a multiple insert would work for two tables the
rely upon autoincrementation of the IDs. In particular, note that in ``1.a`` and ``1.b``
the difference between SQLAlchemy-Exasol and other SQLAlchemy dialects. For some other
SQLAlchemy dialects, they could use something like:

.. code-block:: python

    users = session.scalars(
        insert(User).returning(User),
        bulk_data
    ).all()

This, however, does not work for Exasol and will result in:

.. code-block::

    sqlalchemy.exc.InvalidRequestError: Can't use explicit RETURNING for bulk INSERT
    operation with exasol+exasol.driver.websocket.dbapi2 backend; executemany with
    RETURNING is not enabled for this dialect.

.. literalinclude:: ../../../../examples/features/orm/_2_add_multiple_example_entries.py
       :language: python3
       :caption: examples/features/orm/_2_add_multiple_example_entries.py
