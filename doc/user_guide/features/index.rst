.. _features:

Features
========

Automatic Indexes
-----------------

Exasol is a self-tuning database designed to eliminate the manual effort of performance
optimization. Instead of requiring users to design and maintain indexes, the database
engine intelligently generates them on the fly during query execution to ensure optimal
join and filter performance.

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
