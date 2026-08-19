Connections and Sessions
========================

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

Session Reset
-------------

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
execute additional commands to reset the session as desired, see
:ref:`example_session_reset` in our list of examples.

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
dedicated pool for each user (account, tenant, client).

Exasol offers statement `IMPERSONATE <impersonate_>`_ allowing user
:var:`<U1>` to impersonate another user :var:`<U2>`.  User :var:`<U1>` must
therefore have related privileges for any or a specific user or role to
impersonate.

As the other user :var:`<U2>` usually will not have this privilege, this is a
one-way operation that cannot be reverted.  Hence, when executing this
statement within a given connection, the connection may not be used to
impersonate other users afterward.

In consequence auch a connection may not be suited for further reuse and needs
to be discarded.

.. _impersonate: https://docs.exasol.com/db/latest/sql/impersonate.htm
