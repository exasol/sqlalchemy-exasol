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
def engine(request):
    """Create a basic SQLAlchemy engine for dialect/type integration tests."""
    url = config.db.url.set(drivername=request.param)
    url = url.update_query_dict({"AUTOCOMMIT": "no"})
    test_engine = sa.create_engine(url, poolclass=NullPool, hide_parameters=True)
    try:
        yield test_engine
    finally:
        test_engine.dispose()


@pytest.fixture
def schema_engine(engine):
    return engine


@pytest.fixture
def schema(schema_engine):
    name = "EXA_REG_" + uuid.uuid4().hex[:16].upper()
    with schema_engine.begin() as connection:
        connection.exec_driver_sql(f"CREATE SCHEMA {name}")
    try:
        yield name
    finally:
        with schema_engine.begin() as connection:
            connection.exec_driver_sql(f"DROP SCHEMA {name} CASCADE")
