"""Destructive tests for the dedicated database configured by the test suite.

Run only against a disposable test database with CREATE/DROP SCHEMA and KILL
SESSION privileges, never a shared/customer database. Both aliases retain the
configured database URL's credentials and TLS options. Only test-owned schemas
and sessions are modified; the configured database itself is not dropped.
"""

import datetime as dt
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.pool import NullPool
from sqlalchemy.testing import (
    config,
    fixtures,
)


@pytest.fixture(params=["exa", "exa+websocket"])
def pooled_engine(request):
    if config.db is None:
        pytest.fail("Requires the SQLAlchemy integration test database configuration")
    url = config.db.url.set(drivername=request.param)
    url = url.update_query_dict({"AUTOCOMMIT": "no"})
    engine = sa.create_engine(
        url, pool_pre_ping=True, pool_size=1, max_overflow=0, hide_parameters=True
    )
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def admin_engine(pooled_engine):
    engine = sa.create_engine(
        pooled_engine.url, poolclass=NullPool, hide_parameters=True
    )
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def schema(admin_engine):
    name = "EXA_REG_" + uuid.uuid4().hex[:16].upper()
    with admin_engine.begin() as connection:
        connection.exec_driver_sql(f"CREATE SCHEMA {name}")
    try:
        yield name
    finally:
        with admin_engine.begin() as connection:
            connection.exec_driver_sql(f"DROP SCHEMA {name} CASCADE")


class WebsocketRecovery(fixtures.TestBase):
    @pytest.mark.parametrize("precision,fraction", [(3, 123000), (6, 123456), (6, 1)])
    def test_typed_timestamp_preserves_server_fraction(
        self, pooled_engine, schema, precision, fraction
    ):
        engine = pooled_engine
        expected = dt.datetime(2026, 9, 11, 12, 34, 56, fraction)
        with engine.begin() as connection:
            # Before 8.32, TIMESTAMP(6) was an alias for millisecond precision.
            # Keep the millisecond regression on every supported server.
            # https://docs.exasol.com/db/latest/changelogs/13712.htm
            if precision > 3 and engine.dialect.server_version_info < (8, 32, 0):
                pytest.skip("Microsecond storage requires Exasol >= 8.32")
            connection.exec_driver_sql(
                f"CREATE TABLE {schema}.T (ID INT, TS TIMESTAMP({precision}))"
            )
        table = sa.Table(
            "t", sa.MetaData(), schema=schema.lower(), autoload_with=engine
        )
        with engine.begin() as connection:
            # Exercise the typed bind and reflected result processors together.
            connection.execute(
                table.insert(), [{"id": 1, "ts": expected}, {"id": 2, "ts": None}]
            )
            # Independently seeded literal rules out a compensating bind/result bug.
            connection.exec_driver_sql(
                f"INSERT INTO {schema}.T VALUES (3, TIMESTAMP '{expected.isoformat(sep=' ')}')"
            )
        with engine.connect() as connection:
            raw = connection.exec_driver_sql(
                f"SELECT TS FROM {schema}.T WHERE ID=1"
            ).scalar_one()
            assert dt.datetime.fromisoformat(raw) == expected
            assert connection.execute(
                sa.select(table.c.ts).order_by(table.c.id)
            ).scalars().all() == [expected, None, expected]

    def test_first_checkout_pre_ping_recovers_without_application_retry(
        self, pooled_engine, admin_engine, schema
    ):
        engine = pooled_engine
        with engine.begin() as connection:
            connection.exec_driver_sql(f"CREATE TABLE {schema}.T (ID INT)")
            connection.exec_driver_sql(f"INSERT INTO {schema}.T VALUES (1)")
        with engine.connect() as connection:
            old = connection.exec_driver_sql("SELECT CURRENT_SESSION").scalar_one()
        with admin_engine.begin() as connection:
            # Only kill the idle session that THIS engine just returned to its pool.
            connection.exec_driver_sql(f"KILL SESSION {int(old)}")
        # No try/retry/dispose/invalidate: the very first checkout must work.
        with engine.connect() as connection:
            assert (
                connection.exec_driver_sql("SELECT CURRENT_SESSION").scalar_one() != old
            )
            assert (
                connection.exec_driver_sql(
                    f"SELECT COUNT(*) FROM {schema}.T"
                ).scalar_one()
                == 1
            )

    def test_disconnect_does_not_replay_uncommitted_write(
        self, pooled_engine, admin_engine, schema
    ):
        engine = pooled_engine
        with engine.begin() as connection:
            connection.exec_driver_sql(f"CREATE TABLE {schema}.T (ID INT)")
        with engine.connect() as connection:
            old = connection.exec_driver_sql("SELECT CURRENT_SESSION").scalar_one()
            connection.exec_driver_sql(f"INSERT INTO {schema}.T VALUES (1)")
            with admin_engine.begin() as killer:
                killer.exec_driver_sql(f"KILL SESSION {int(old)}")
            with pytest.raises(sa.exc.DBAPIError) as caught:
                connection.exec_driver_sql(f"INSERT INTO {schema}.T VALUES (2)")
            assert caught.value.connection_invalidated
            # SQLAlchemy requires rollback of the lost transaction; no replay.
            connection.rollback()
        with engine.connect() as connection:
            assert (
                connection.exec_driver_sql(
                    f"SELECT COUNT(*) FROM {schema}.T"
                ).scalar_one()
                == 0
            )

    def test_server_error_does_not_invalidate_healthy_connection(
        self, pooled_engine, schema
    ):
        engine = pooled_engine
        with engine.connect() as connection:
            old = connection.exec_driver_sql("SELECT CURRENT_SESSION").scalar_one()
            with pytest.raises(sa.exc.DBAPIError) as caught:
                connection.exec_driver_sql(f"SELECT * FROM {schema}.DOES_NOT_EXIST")
            assert not caught.value.connection_invalidated
            connection.rollback()
            assert (
                connection.exec_driver_sql("SELECT CURRENT_SESSION").scalar_one() == old
            )
