.. _features:

Features
========

Object-Relational Mapping
-------------------------

SQLAlchemy-Exasol utilizes the Object-Relational Mapping (ORM) interface provided by
SQLAlchemy. ORM is a powerful tool that maps database tables to Python classes, allowing
developers to interact with relational databases using object-oriented code instead of
raw SQL. It is highly useful because it abstracts away complex database interactions,
such as connection management and transaction handling, into a "Unit of Work" pattern
that ensures data consistency.

.. note::

    * To get started, check out our :ref:`examples_orm`.
    * For more examples & details, see SQLAlchemy's
      `ORM Quick Start <https://docs.sqlalchemy.org/en/20/orm/quickstart.html>`__
      and `ORM Index <https://docs.sqlalchemy.org/en/20/orm/index.html>`__.
