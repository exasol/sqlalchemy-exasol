from contextlib import contextmanager

import pyexasol
import pytest
from sqlalchemy.dialects import registry

registry.register("exa.pyodbc", "sqlalchemy_exasol.pyodbc", "EXADialect_pyodbc")
registry.register("exa.turbodbc", "sqlalchemy_exasol.turbodbc", "EXADialect_turbodbc")

# Suppress spurious warning from pytest
pytest.register_assert_rewrite("sqlalchemy.testing.assertions")

from sqlalchemy.testing.plugin.pytestplugin import *
from sqlalchemy.testing.plugin.pytestplugin import (
    pytest_sessionfinish as _pytest_sessionfinish,
)
from sqlalchemy.testing.plugin.pytestplugin import (
    pytest_sessionstart as _pytest_sessionstart,
)

_TEST_SCHEMA = "TEST"


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
        con.execute(f"DROP SCHEMA IF EXISTS {_TEST_SCHEMA} CASCADE;")
        con.execute(f"CREATE SCHEMA {_TEST_SCHEMA};")
        con.commit()

    _pytest_sessionstart(session)


def pytest_sessionfinish(session):
    with _connection() as con:
        con.execute(f"DROP SCHEMA IF EXISTS {_TEST_SCHEMA} CASCADE;")
        con.commit()

    _pytest_sessionfinish(session)
