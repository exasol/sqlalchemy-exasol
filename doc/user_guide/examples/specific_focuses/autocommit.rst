.. _autocommit:

Autocommit
==========

These examples are meant to highlight best practices and allow users to explore the
difference between having ``AUTOCOMMIT`` enabled versus disabled.

Throughout our examples, we use ``engine.begin()``. Code inside of a with-block using
``engine.begin()`` will behave the same whether ``AUTOCOMMIT``
is enabled (``y``) or disabled (``n``). This is because ``engine.begin()`` automatically
issues a ``COMMIT`` when the block successfully finished or a ``ROLLBACK`` if it fails.
For any basic database modifications, the recommended best practice is to use
``engine.begin()``. This is to ensure that the objects are in the desired state before
performing further manipulation steps. While it is possible to use ``engine.connect()``
instead, when ``AUTOCOMMIT`` is disabled, you must manually, inside of the with-block,
call ``commit()``. For a more nuanced discussion, see :ref:`begin_or_connect`.

To explore what changes when ``AUTOCOMMIT`` is set to ``n``, you can:

1. Modify your configuration file, as described on :ref:`example_configuration`, to set
   ``"AUTOCOMMIT":"n"``.
2. Modify the code in the examples to use ``engine.connect()`` instead of
   ``engine.begin()``.
3. Try to execute the examples and see what happens. You should get failures, as
   ``engine.connect()`` without ``AUTOCOMMIT`` requires you to manually call
   ``conn.commit()`` as needed.
4. Add ``conn.commit()`` to the examples and try to execute them. They should now pass.

.. note::

    The examples on this page are presented in sections, but they are all part
    of the same module ``examples/features/specific_focuses/_1_autocommit.py``.
    They are broken up here to provide further information and context. Please
    ensure that you read and execute the parts in order.


.. _ddl:

Data Definition Language (DDL)
------------------------------

.. literalinclude:: ../../../../examples/features/specific_focuses/_1_autocommit.py
       :language: python3
       :caption: examples/features/specific_focuses/_1_autocommit.py
       :end-before: # 2. Data Query Language (DQL)


It is recommended to use ``engine.begin()`` for DDL statements.

.. note::

    Note that ``IDENTITY``
    (`an Exasol Database keyword <https://docs.exasol.com/db/latest/sql_references/data_types/identitycolumns.htm?Highlight=identity>`__)
    **must** be included for the ID to autoincrement. This is not required for the
    examples given in :ref:`examples_non_orm` or :ref:`examples_orm`, where SQLAlchemy
    generates the required SQL statement for the Exasol database instance.

Data Query Language (DQL)
-------------------------

.. literalinclude:: ../../../../examples/features/specific_focuses/_1_autocommit.py
       :language: python3
       :caption: examples/features/specific_focuses/_1_autocommit.py
       :start-at: # 2. Data Query Language (DQL)
       :end-before: # 3. Data Manipulation Language (DML)

Typically, ``SELECT`` is considered the only member of DQL. In such use cases, no data
manipulations are occurring, so no manual commits need to be made. As such,
this code works and should stay the same regardless of whether ``AUTOCOMMIT`` is
enabled or disabled.

Data Manipulation Language (DML)
--------------------------------

.. literalinclude:: ../../../../examples/features/specific_focuses/_1_autocommit.py
       :language: python3
       :caption: examples/features/specific_focuses/_1_autocommit.py
       :start-at: # 3. Data Manipulation Language (DML)

Like the :ref:`ddl` example, it is preferred here to use ``begin()`` in the with-block.
This behaves the same whether ``AUTOCOMMIT`` is enabled or disabled. For a
more nuanced discussion, see :ref:`begin_or_connect`.

.. _begin_or_connect:


Connection Management in SQLAlchemy
-----------------------------------

.. _begin-method:

The ``begin()`` Method
^^^^^^^^^^^^^^^^^^^^^^

The ``begin()`` method provides a **transactional boundary**. It is the safest choice
for an operation that modifies the database.

.. list-table:: When to use ``begin()``
   :widths: 30 70
   :header-rows: 1

   * - Scenario
     - Description
   * - DDL
     - Use for ``CREATE``, ``ALTER``, or ``DROP`` commands to ensure schema changes are committed.
   * - DML
     - Ideal for ``INSERT``, ``UPDATE``, and ``DELETE`` where you want an "all-or-nothing" result.
   * - Auto-Rollback
     - If your code fails mid-block, SQLAlchemy automatically reverts any partial changes.

.. _connect-method:

The ``connect()`` Method
^^^^^^^^^^^^^^^^^^^^^^^^

The ``connect()`` method provides a **raw connection**. It offers granular control but
places the responsibility of transaction management on the user.

When ``AUTOCOMMIT`` is enabled, using ``connect()`` ensures that each statement is
finalised by the database as soon as it is executed. If ``AUTOCOMMIT`` is disabled,
then you must manually use ``commit``.

.. list-table:: When to use ``connect()``
   :widths: 30 70
   :header-rows: 1

   * - Scenario
     - Description
   * - DQL
     - Best for ``SELECT`` statements where no data is being changed.
   * - DML
     - Use if you need to commit specific parts of a long-running script at different times.
   * - Performance Tuning
     - Avoids the overhead of starting a transaction block when only reading data.
