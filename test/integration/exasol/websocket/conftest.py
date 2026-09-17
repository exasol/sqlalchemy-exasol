import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.pool import NullPool
from sqlalchemy.testing import config


@pytest.fixture(
    params=[
        pytest.param("exa", id="exa-driver"),
        pytest.param("exa+websocket", id="websocket-driver"),
    ]
)
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
