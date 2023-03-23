from contextlib import contextmanager

import pyexasol
import pytest
from sqlalchemy.dialects import registry

registry.register("exa.pyodbc", "sqlalchemy_exasol.pyodbc", "EXADialect_pyodbc")
registry.register("exa.turbodbc", "sqlalchemy_exasol.turbodbc", "EXADialect_turbodbc")
registry.register(
    "exa.websocket", "sqlalchemy_exasol.websocket", "EXADialect_websocket"
)

# Suppress spurious warning from pytest
pytest.register_assert_rewrite("sqlalchemy.testing.assertions")

from sqlalchemy.testing.plugin.pytestplugin import *
from sqlalchemy.testing.plugin.pytestplugin import (
    pytest_sessionfinish as _pytest_sessionfinish,
)
from sqlalchemy.testing.plugin.pytestplugin import (
    pytest_sessionstart as _pytest_sessionstart,
)

_TEST_SCHEMAS = ["TEST", "TEST_SCHEMA", "TEST_SCHEMA2"]


@contextmanager
def _connection(dsn="localhost:8888", user="SYS", password="exasol"):
    connection = pyexasol.connect(
        dsn=dsn,
        user=user,
        password=password,
    )
    yield connection
    connection.close()


def pytest_sessionstart(session):
    with _connection() as con:
        for schema in _TEST_SCHEMAS:
            con.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE;")
            con.execute(f"CREATE SCHEMA {schema};")
        con.commit()

    _pytest_sessionstart(session)


def pytest_sessionfinish(session):
    with _connection() as con:
        for schema in _TEST_SCHEMAS:
            con.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE;")
        con.commit()

    _pytest_sessionfinish(session)
