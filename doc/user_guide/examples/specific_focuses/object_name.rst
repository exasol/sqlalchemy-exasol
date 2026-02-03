.. _object_name:

Object Name Handling
====================

When passing an object name, like a table name, into a SQLAlchemy construct,
the name usage is case-insensitive. You could define the ``table_name_lower`` in
uppercase or lowercase.

.. literalinclude:: ../../../../examples/features/specific_focuses/_2_object_name.py
       :language: python3
       :caption: examples/features/specific_focuses/_2_object_name
       :end-before: # 2. Select with Fully Prepared Raw SQL Statement

When using a fully prepared raw SQL statement or using a where clause, you must
ensure to send the text as it was saved in the Exasol database instance. In the
case of table & schema names, these are always saved in **uppercase**.

.. literalinclude:: ../../../../examples/features/specific_focuses/_2_object_name.py
       :language: python3
       :caption: examples/features/specific_focuses/_2_object_name
       :start-at: # 2. Select with Fully Prepared Raw SQL Statement
