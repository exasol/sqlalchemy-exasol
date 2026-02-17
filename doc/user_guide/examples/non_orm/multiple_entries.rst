.. _example_non_orm_multiple_entries:

Working with Multiple Entries
=============================

This script inserts multiple entries into our two tables in one session & relies
on in-session auto-incrementing behavior. As mentioned in the :ref:`known_limitations`,
SQLAlchemy is slower than other drivers at performing multiple entry inserts.

.. literalinclude:: ../../../../examples/features/non_orm/_2_working_with_multiple_entries.py
       :language: python3
       :caption: examples/features/non_orm/_2_working_with_multiple_entries.py
