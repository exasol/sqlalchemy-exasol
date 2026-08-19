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

Connections and Sessions, Session Reset
---------------------------------------

Normally a connection is tied to a *database session*.  Hence, when the
Connection Pool *reuses* a connection, the resp. session is reused, too.

.. Warning::

   Depending on your use case this may be inadequate or even problematic if
   users have different permissions or session settings.

Additionally, both aspects can change over time, i.e. a user gets granted more
or less permissions than before or session parameters are updated with SQL
command `ALTER SESSION <alter_session_>`_.

Ultimately, the desired policy needs to be implemented by the *application*
using the connection pool incl. whether the resp. database session should be
reused or not.

Tied to a session are

* Transactions: SQLAlchemy parameter `reset_on_return <reset_on_return_>`_
  supports to either commit or rollback open transaction when returning a
  connection to the pool.
* Changes with SQL command ``ALTER SESSION``
* The Current user, see section :ref:`change_user` below.
* Temporary objects: Not available in Exasol

.. _reset_on_return:
   https://docs.sqlalchemy.org/en/20/core/pooling.html#sqlalchemy.pool.Pool.params.reset_on_return
.. _alter_session:
   https://docs.exasol.com/db/latest/sql/alter_session.htm

Currently there is no command in Exasol to reset the current session.

However, the application could listen to an appropriate event, e.g. `checkin
<checkin_>`_, `checkout <checkout_>`_, or `reset <reset_>`_ and manually
execute additional commands to reset the session as desired.

.. _checkin:
   https://docs.sqlalchemy.org/en/20/core/events.html#sqlalchemy.events.PoolEvents.checkin
.. _checkout:
   https://docs.sqlalchemy.org/en/20/core/events.html#sqlalchemy.events.PoolEvents.checkout
.. _reset:
   https://docs.sqlalchemy.org/en/20/core/events.html#sqlalchemy.events.PoolEvents.reset

.. _change_user:

Changing the User for an Existing Connection
--------------------------------------------

.. role:: var

SQLAlchemy API does not allow altering the user for an existing connection.
The same applies to MySQL Pooling.  Instead, the application could use a
dedicated pool for each user (account, tenant, client).  ``psycopg`` for
PostgreSQL offers an argument ``key`` that could be used for this purpose.

Exasol offers statement `IMPERSONATE <impersonate_>`_ allowing user
:var:`<U1>` to impersonate another user :var:`<U2>`.

* User :var:`<U1>` must therefore have related privileges for any or a specific
  user or role to impersonate.
* As the other user :var:`<U2>` usually will not have this privilege, this is a
  one-way operation that cannot be reverted.

As the selected user to impersonate usually will not have this privilege, this
is a one-way operation that cannot be reverted.  Hence, when executing this
statement within a given connection, the connection may not be used to
impersonate other users afterward.

.. _impersonate: https://docs.exasol.com/db/latest/sql/impersonate.htm
