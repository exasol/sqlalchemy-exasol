"""Opt-in, destructive only to test-owned resources on a disposable Exasol server.

EXASOL_TEST_URL must name a dedicated test server/user with CREATE SCHEMA and
KILL SESSION privileges. Never point this suite at a shared/customer database.
The provided URL's credentials/TLS options are retained; both aliases are tested.
Run with --noconftest to avoid unrelated integration fixture initialization.
"""

import datetime as dt
import os
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.pool import NullPool


@pytest.fixture(params=["exa", "exa+websocket"])
def engines(request):
    value = os.environ.get("EXASOL_TEST_URL")
    if not value:
        pytest.skip("EXASOL_TEST_URL must explicitly opt into disposable live testing")
    url = sa.make_url(value).set(drivername=request.param)
    url = url.update_query_dict({"AUTOCOMMIT": "no"})
    pooled = sa.create_engine(
        url, pool_pre_ping=True, pool_size=1, max_overflow=0, hide_parameters=True
    )
    admin = sa.create_engine(url, poolclass=NullPool, hide_parameters=True)
    try:
        yield pooled, admin
    finally:
        pooled.dispose()
        admin.dispose()


@pytest.fixture
def schema(engines):
    _, admin = engines
    name = "EXA_REG_" + uuid.uuid4().hex[:16].upper()
    with admin.begin() as connection:
        connection.exec_driver_sql(f"CREATE SCHEMA {name}")
    try:
        yield name
    finally:
        with admin.begin() as connection:
            connection.exec_driver_sql(f"DROP SCHEMA {name} CASCADE")


@pytest.mark.parametrize("precision,fraction", [(3, 123000), (6, 123456), (6, 1)])
def test_typed_timestamp_preserves_server_fraction(
    engines, schema, precision, fraction
):
    engine, _ = engines
    expected = dt.datetime(2026, 9, 11, 12, 34, 56, fraction)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            f"CREATE TABLE {schema}.T (ID INT, TS TIMESTAMP({precision}))"
        )
    table = sa.Table("t", sa.MetaData(), schema=schema.lower(), autoload_with=engine)
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


def test_first_checkout_pre_ping_recovers_without_application_retry(engines, schema):
    engine, admin = engines
    with engine.begin() as connection:
        connection.exec_driver_sql(f"CREATE TABLE {schema}.T (ID INT)")
        connection.exec_driver_sql(f"INSERT INTO {schema}.T VALUES (1)")
    with engine.connect() as connection:
        old = connection.exec_driver_sql("SELECT CURRENT_SESSION").scalar_one()
    with admin.begin() as connection:
        # Only kill the idle session that THIS engine just returned to its pool.
        connection.exec_driver_sql(f"KILL SESSION {int(old)}")
    # No try/retry/dispose/invalidate: the very first checkout must work.
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT CURRENT_SESSION").scalar_one() != old
        assert (
            connection.exec_driver_sql(f"SELECT COUNT(*) FROM {schema}.T").scalar_one()
            == 1
        )


def test_disconnect_does_not_replay_uncommitted_write(engines, schema):
    engine, admin = engines
    with engine.begin() as connection:
        connection.exec_driver_sql(f"CREATE TABLE {schema}.T (ID INT)")
    with engine.connect() as connection:
        old = connection.exec_driver_sql("SELECT CURRENT_SESSION").scalar_one()
        connection.exec_driver_sql(f"INSERT INTO {schema}.T VALUES (1)")
        with admin.begin() as killer:
            killer.exec_driver_sql(f"KILL SESSION {int(old)}")
        with pytest.raises(sa.exc.DBAPIError) as caught:
            connection.exec_driver_sql(f"INSERT INTO {schema}.T VALUES (2)")
        assert caught.value.connection_invalidated
        # SQLAlchemy requires rollback of the lost transaction; no replay.
        connection.rollback()
    with engine.connect() as connection:
        assert (
            connection.exec_driver_sql(f"SELECT COUNT(*) FROM {schema}.T").scalar_one()
            == 0
        )


def test_server_error_does_not_invalidate_healthy_connection(engines, schema):
    engine, _ = engines
    with engine.connect() as connection:
        old = connection.exec_driver_sql("SELECT CURRENT_SESSION").scalar_one()
        with pytest.raises(sa.exc.DBAPIError) as caught:
            connection.exec_driver_sql(f"SELECT * FROM {schema}.DOES_NOT_EXIST")
        assert not caught.value.connection_invalidated
        connection.rollback()
        assert connection.exec_driver_sql("SELECT CURRENT_SESSION").scalar_one() == old
