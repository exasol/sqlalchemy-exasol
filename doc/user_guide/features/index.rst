.. _features:

Features
========

Autocommit
----------

By default SQLAlchemy-Exasol has ``AUTOCOMMIT`` turned on, as mentioned in
:ref:`dialect_specific_params`. This means that every statement is executed and
finalized by the database immediately after leaving a with-block.

* Our :ref:`autocommit` examples
* SQLAlchemy's `Working with Engines and Connections <https://docs.sqlalchemy.org/en/20/core/connections.html>`__
* SQLAlchemy's `Transaction & Connection Management <https://docs.sqlalchemy.org/en/20/orm/session_transaction.html>`__

Autoincremented Columns
-----------------------

In SQLAlchemy-Exasol, the autoincrement feature leverages Exasol's native
`IDENTITY <https://docs.exasol.com/db/latest/sql_references/data_types/identitycolumns.htm>`__
columns to automatically generate unique, sequential primary key values. To enable this
behavior when defining a table, set ``primary_key=True`` as shown in the following examples:

* :ref:`Create Table <example_non_orm_create_table>`
* :ref:`Create Table with ORM <example_orm_create_table>`

Once configured, Exasol generates a new ID on the server side whenever a new row is
inserted.

Automatic Indexes
-----------------

Exasol is a self-tuning database designed to eliminate the manual effort of performance
optimization. Instead of requiring users to design and maintain indexes, the database
engine intelligently generates and updates them on the fly during query execution to ensure
optimal join and filter performance.

For SQLALchemy-Exasol users, this means:

* **Simplified Development**: You are free from the burden of manual index
  management; the database handles it all for you.
* **Automatic Performance**: Efficient indexes are created precisely when needed and
  are automatically maintained or discarded based on usage.
* **Optimized Storage**: Indexes are only persisted upon a successful transaction
  commit, keeping your database clean and efficient.

Because Exasol provides this built-in auto-tuning, manual index creation is not only
unnecessary but intentionally unsupported to prevent interference with the engine's
optimization algorithms. For more in-depth information, explore the Exasol documentation
on `indexes <https://docs.exasol.com/db/latest/performance/indexes.htm>`__.

Caching
-------

Since version 1.4, SQLAlchemy features a "SQL compilation caching" facility designed to
significantly reduce Python interpreter overhead during query construction. This system
works by generating a unique cache key that represents the structural state of a Core or
an ORM SQL construct, including its columns, tables, and JOIN conditions. Once a
specific query structure is compiled into a string for the first time, SQLAlchemy stores
the result in an internal cache; subsequent executions with the same structure skip the
expensive string compilation process and reuse the existing SQL. This is particularly
beneficial for ORM-heavy applications, as it streamlines the logic for lazy loaders and
relationship lookups.

For more information, see these pages from SQLAlchemy:

* `Performance <https://docs.sqlalchemy.org/en/21/faq/performance.html>`__
* `SQL Compilation Caching <https://docs.sqlalchemy.org/en/21/core/connections.html#sql-compilation-caching>`__

Since version 1.4, SQLAlchemy has also streamlined its "Reflection API" by implementing
an internal metadata cache within the Inspector object. This system is designed to
minimize the performance cost of querying database system catalogs—such as those in
Exasol—by ensuring that schema details like columns, foreign keys, and constraints are
only fetched once per inspector instance. When a method like ``get_foreign_keys()`` is
called, the result is stored in an internal dictionary; subsequent requests for the same
table metadata skip the network round-trip and return the cached data immediately.
This is particularly advantageous for applications that perform heavy reflection
operations.

For more details, see:

* `Reflecting Database Objects <https://docs.sqlalchemy.org/en/21/core/reflection.html>`__

Foreign Keys
------------

By default, Exasol does not enforce foreign keys or primary keys. Instead, they are
primarily used as metadata to help the query optimizer create faster execution plans:

* **Default State**: By default, constraints are created in a ``DISABLE`` state. This
  means you can insert data that violates referential integrity without the database
  stopping you.
* **Enforcement Setting**: To prevent invalid data from being inserted, you can
  explicitly set the constraint to ``ENABLE``.
* **Performance Impact**: Exasol leaves them disabled by default because strict
   enforcement adds overhead during high-speed data loading (DML operations).

To see the status of your foreign key columns, check table
`EXA_ALL_CONSTRAINTS <https://docs.exasol.com/db/latest/sql_references/system_tables/metadata/exa_all_constraints.htm>`__.

To check what your system settings are, use this SQL statement:

.. code-block:: sql

    SELECT * FROM EXA_PARAMETERS
    WHERE PARAMETER_NAME = 'CONSTRAINT_STATE_DEFAULT';


To check a foreign key constraint without switching the constraint to ``ENABLE``, see
`Verification of the Foreign Key Property <https://docs.exasol.com/db/latest/sql/foreignkey.htm>`__.

To switch a constraint to ``ENABLE``, choose which SQL statement suits your purposes best:

.. code-block:: sql

    -- For a specific constraint
    ALTER TABLE <table_name> MODIFY CONSTRAINT <constraint_name> ENABLE;

    -- For global enforcement, which will degrade performance
    ALTER SYSTEM SET DEFAULT_CONSTRAINT_STATE = 'ENABLE';


.. _orm:

Object-Relational Mapping
-------------------------

SQLAlchemy-Exasol utilizes the Object-Relational Mapping (ORM) interface provided by
SQLAlchemy. ORM is a powerful tool that maps database tables to Python classes, allowing
developers to interact with relational databases using object-oriented code instead of
raw SQL. It is highly useful because it abstracts away complex database interactions,
such as connection management and transaction handling, into a "Unit of Work" pattern
that ensures data consistency.

.. note::

    * To get started, check out our :ref:`ORM Examples <examples_orm>`.
    * For more examples & details, see SQLAlchemy's
      `ORM Quick Start <https://docs.sqlalchemy.org/en/20/orm/quickstart.html>`__
      and `ORM Index <https://docs.sqlalchemy.org/en/20/orm/index.html>`__.
