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


class TestConfigurationError(Exception):
    """Error in test configuration setup."""


@pytest.fixture
def config_url() -> sqlalchemy.URL:
    if config.db:
        return config.db.url
    raise TestConfigurationError("config.db is None")


class Listener:
    def __init__(self, target: sqlalchemy.event.EventTarget):
        self._target = target
        self.connection_ids: set[str] = set()
        self.results: list[Any] = []

    def _on_checkout(self, dbapi_conn, connection_rec, connection_proxy):
        self.connection_ids.add(id(dbapi_conn))

    def listen(self, event: str) -> Listener:
        sqlalchemy.event.listen(self._target, event, self._on_checkout)
        return self

    def unlisten(self, event: str) -> Listener:
        sqlalchemy.event.remove(self._target, event, self._on_checkout)
        return self


class Scenario:
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
        def result(con: sqlalchemy.Connection) -> Any:
            row = con.execute(sqlalchemy.text(statement)).fetchone()
            return row[0] if row else None

        return [result(c) for c in connections]

    @contextlib.contextmanager
    def listen(self, event: str):
        listener = Listener(self._engine).listen(event)
        yield listener
        listener.unlisten(event)

    def round_trip(self, sql_statement: str) -> Listener:
        with self.listen("checkout") as listener:
            connections = self.connect(2)
            listener.results = self.execute(connections, sql_statement)
            self.close(connections)
        return listener


class Pooling(fixtures.TestBase):
    @classmethod
    def exception_trace(cls, ex: Exception) -> Iterator[str]:
        """
        Return a sequence of strings, each representing one of the exceptions
        linked by __cause__ and containing the exceptions's message.
        """

        current: BaseException | None = ex
        cause = "Initial exception"
        while current:
            yield (f"{cause}: {type(current)}: {current}")
            current = current.__cause__
            cause = "Cause"

    @classmethod
    def create_engine(cls, url: sqlalchemy.URL, **kwargs) -> sqlalchemy.Engine:
        args = {
            "poolclass": sqlalchemy.QueuePool,
            "pool_size": 2,
            "max_overflow": 0,
            "pool_recycle": 3600,  # recycle connections after an hour
            "pool_pre_ping": True,  # test connection before reuse
        } | kwargs
        return create_engine(url, **args)

    def test_exception(self, config_url: sqlalchemy.URL) -> None:
        """
        Verify that the exception raised by a SQLALchemy Engine using a
        Connection Pool does not reveal any secret.
        """

        url = config_url.set(password="wrong password")
        engine = self.create_engine(url)
        with pytest.raises(sqlalchemy.exc.DBAPIError) as ex:
            engine.connect()
        trace = "\n".join(self.exception_trace(ex.value))
        assert "wrong password" not in trace

    def test_another_connection_blocks(self, config_url: sqlalchemy.URL) -> None:
        """
        Allocate all connections of the pool. Assert trying to
        ``connect()`` one more time blocks until one of the connections is
        returned to the pool and can be reused.
        """

        def get_another_connection(engine):
            with engine.connect() as con:
                nonlocal result
                result = con.execute(sqlalchemy.text("SELECT 33")).fetchone()[0]

        engine = self.create_engine(config_url)
        result = None
        scenario = Scenario(engine)
        connections = scenario.connect(2)
        thread = threading.Thread(target=get_another_connection, args=(engine,))
        thread.start()
        sleep(1)
        assert thread.is_alive()  # assert threat is blocking

        scenario.close(connections[:1])
        thread.join()
        assert result == 33

    def test_reuse(self, config_url: sqlalchemy.URL) -> None:
        """
        Allocate 2 connections, use and close them and when requesting
        another 2 connections, verify the initial 2 connections are reused.
        """
        engine = self.create_engine(config_url)
        scenario = Scenario(engine)

        round_1 = scenario.round_trip("SELECT 42")
        assert round_1.results == [42, 42]

        known = round_1.connection_ids

        round_2 = scenario.round_trip("SELECT 43")
        assert round_2.results == [43, 43]
        assert round_2.connection_ids.issubset(known)

    def test_recycle(self, config_url: sqlalchemy.URL) -> None:
        """
        Set ``pool_recycle`` to 1 second and verify that connection are
        not reused after this time has passed.
        """
        engine = self.create_engine(config_url, pool_recycle=1)
        scenario = Scenario(engine)

        round_1 = scenario.round_trip("SELECT 42")
        assert round_1.results == [42, 42]

        reuse = round_1.connection_ids
        sleep(2)

        with scenario.listen("checkout") as round_2:
            connections = scenario.connect(1)
            scenario.close(connections)
        assert round_2.connection_ids.isdisjoint(reuse)
