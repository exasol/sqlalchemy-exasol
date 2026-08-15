from __future__ import annotations

import contextlib
import threading
from collections.abc import Iterator
from time import sleep
from typing import Any

import pytest
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.testing import (
    config,
    fixtures,
)


class Listener:
    def __init__(self, target: sqlalchemy.event.EventTarget):
        self._target = target
        self.connection_ids: set[str] = set()

    def _on_checkout(self, dbapi_conn, connection_rec, connection_proxy):
        self.connection_ids.add(id(dbapi_conn))

    def listen(self, event: str) -> Listener:
        sqlalchemy.event.listen(self._target, event, self._on_checkout)
        return self

    def unlisten(self, event: str) -> Listener:
        sqlalchemy.event.remove(self._target, event, self._on_checkout)


class Bench:
    def __init__(self, engine: sqlalchemy.Engine):
        self._engine = engine

    def connect(self, n: int) -> list[sqlalchemy.Connection]:
        return [self._engine.connect() for _ in range(n)]

    def close(self, connections: list[sqlalchemy.Connection]) -> None:
        for con in connections:
            con.close()

    def execute(
        self,
        connections: list[sqlalchemy.Connection],
        statement: str,
    ) -> list[Any]:
        return [
            c.execute(sqlalchemy.text(statement)).fetchone()[0] for c in connections
        ]

    @contextlib.contextmanager
    def listen(self, event: str):
        listener = Listener(self._engine).listen(event)
        yield listener
        listener.unlisten(event)


class Pooling(fixtures.TestBase):
    @classmethod
    def exception_trace(cls, ex: Exception) -> Iterator[str]:
        """
        Return a sequence of strings, each representing one of the exceptions
        linked by __cause__ and containing the exceptions's message.
        """

        current = ex
        cause = "Initial exception"
        while current:
            yield (f"{cause}: {type(current)}: {current}")
            current = current.__cause__
            cause = "Cause"

    @classmethod
    def create_engine(cls, **kwargs) -> sqlalchemy.Engine:
        args = {
            "url": config.db.url,
            "poolclass": sqlalchemy.QueuePool,
            "pool_size": 2,
            "max_overflow": 0,
            "pool_recycle": 3600,  # recycle connections after an hour
            "pool_pre_ping": True,  # test connection before reuse
        } | kwargs
        return create_engine(**args)

    def test_exception(self) -> None:
        """
        Verify that the exception raised by a SQLALchemy Engine using a
        Connection Pool does not reveal any secret.
        """

        url = config.db.url.set(password="wrong password")
        engine = self.create_engine(url=url)
        with pytest.raises(sqlalchemy.exc.DBAPIError) as ex:
            engine.connect()
        trace = "\n".join(self.exception_trace(ex.value))
        assert "wrong password" not in trace

    def test_third_connection_blocks(self) -> None:
        """
        Allocate all connections of the pool. Assert subsequent
        ``connect()`` blocks until one of the connections is returned to the
        pool.
        """

        def get_third_connection(engine):
            with engine.connect() as con:
                nonlocal result
                result = con.execute(sqlalchemy.text("SELECT 33")).fetchone()[0]

        engine = self.create_engine()
        result = None
        bench = Bench(engine)
        connections = bench.connect(2)
        thread = threading.Thread(target=get_third_connection, args=(engine,))
        thread.start()
        sleep(1)
        assert thread.is_alive()  # assert threat is blocking

        bench.close(connections[:1])
        thread.join()
        assert result == 33
