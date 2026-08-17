.. _example_connection_pooling:

Connection Pooling
==================

You can instantiate a pool directly or more conveniently when creating a
SQLAlchemy Engine. The following example creates a SQLAlchemy engine using a
``QueuePool`` (which is the default) and a pool size of max. 10
connections.

Parameter ``max_overflow=2`` adds another 2 connections that are not managed
for reuse.  Parameter ``pool_recycle`` limits the life time of cached
connections, and ``pool_pre_ping`` requests the pool to check each connection
before reuse.

.. literalinclude:: ../../../../examples/features/specific_focuses/_5_connection_pooling.py
       :language: python
       :caption: examples/features/specific_focuses/_5_connection_pooling.py

``engine.connect()`` returns a ``sqlalchemy.engine.Connection`` that may be
fresh or reused.
