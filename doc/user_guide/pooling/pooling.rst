Connection Pooling
==================

This chapter gives a tutorial for pooling Exasol connections in Python.

Creating a database connection can be slow. Connection pooling is a way to
reuse existing connections instead of opening and closing a new one for every
request.

Exasol recommends using `SQLAlchemy Connection Pooling <sqla_pooling_>`_ for
the following reasons:

* SQLAlchemy is very popular, well-maintained, and documented.
* SQLAlchemy Connection Pooling is convenient, advanced, and provides
  a rich and established feature set.

SQLAlchemy provides `different Pool implementations <variants_>`_ extending
the abstract class ``sqlalchemy.Pool``.  The most versatile is the `QueuePool
<queue_pool_>`_, limiting the number of open connections.

.. _sqla_pooling:
   https://docs.sqlalchemy.org/en/21/core/pooling.html
.. _variants:
   https://docs.sqlalchemy.org/en/21/core/pooling.html#api-documentation-available-pool-implementations
.. _queue_pool:
   https://docs.sqlalchemy.org/en/21/core/pooling.html#sqlalchemy.pool.QueuePool

Creating a Connection Pool
--------------------------

See :ref:`example_connection_pooling` in our list of examples.

Stale Connections
-----------------

For discarding stale connections and freeing the resources allocated by them,
SQLALchemy pools offer methods `Pool.dispose() <pool_dispose_>`_ and
`Pool.recreate() <pool_recreate_>`_.

.. _pool_dispose:
   https://docs.sqlalchemy.org/en/21/core/pooling.html#sqlalchemy.pool.Pool.dispose
.. _pool_recreate:
   https://docs.sqlalchemy.org/en/21/core/pooling.html#sqlalchemy.pool.Pool.recreate

For avoiding stale connections, you can set a timeout with engine option
`pool_recycle <pool_recycle_>`_ or use option `pool_pre_ping <pre_ping_>`_
which invokes the DBAPI-specific ``ping()`` method, or uses SQL statement
``SELECT 1``

.. _pre_ping:
   https://docs.sqlalchemy.org/en/21/core/pooling.html#disconnect-handling-pessimistic
.. _pool_recycle:
   https://docs.sqlalchemy.org/en/21/core/pooling.html#sqlalchemy.pool.Pool.params.recycle

Errors
------

Invalid credentials will raise an error in SQLAlchemy as shown below, chained
with ``__cause__``. The password is not revealed.

.. code-block:: shell

    Initial exception: <class 'sqlalchemy.exc.DBAPIError'>:
      (exasol.driver.websocket._errors.Error)
      (Background on this error at: https://sqlalche.me/e/20/dbapi)
    __cause__: <class 'exasol.driver.websocket._errors.Error'>:
    __cause__: <class 'pyexasol.exceptions.ExaAuthError'>:
    (
        message     =>  Connection exception - authentication failed.
        dsn         =>  127.0.0.1/nocertcheck:8563
        user        =>  sys
        schema      =>
        session_id  =>
        code        =>  08004
    )

Events
------

You can use SQLAlchemy's `Pool Events <pool_events_>`_ to react on each time a
connection is checked out or handed back to the pool, see
:ref:`example_connection_pooling` in our list of examples.

.. _pool_events:
   https://docs.sqlalchemy.org/en/20/core/events.html#sqlalchemy.events.PoolEvents
