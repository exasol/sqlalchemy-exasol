.. _object_name:

Object Name Handling
====================

When passing an object name, e.g. the name of a database table, into a SQLAlchemy construct,
the name usage is case-insensitive.  You could pass ``table_name.lower()``
or  ``table_name.upper()`` as the first argument to ` `Table()`` in the following example,
and both options will work.

.. literalinclude:: ../../../../examples/features/specific_focuses/_2_object_name.py
       :language: python3
       :caption: examples/features/specific_focuses/_2_object_name.py
       :end-before: # 2. Select with fully prepared raw SQL statement

When using a fully prepared raw SQL statement or using a where clause, you must
ensure to send the text as it was saved in the Exasol database instance. In the
case of table & schema names, these are always saved in **uppercase**.

.. literalinclude:: ../../../../examples/features/specific_focuses/_2_object_name.py
       :language: python3
       :caption: examples/features/specific_focuses/_2_object_name.py
       :start-at: # 2. Select with fully prepared raw SQL statement
