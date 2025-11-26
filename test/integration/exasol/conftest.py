import ssl
from contextlib import contextmanager

import pyexasol
import pytest
from sqlalchemy.dialects import registry

registry.register(
    "exa.websocket", "sqlalchemy_exasol.websocket", "EXADialect_websocket"
)

# Suppress spurious warning from pytest
pytest.register_assert_rewrite("sqlalchemy.testing.assertions")

# Attention:
# The code duplication in regard to `/test/sqlalchemy/conftest.py` # can be removed
# once we have cut the dependency to the sqla test framework/plugin # for our own tests.
from sqlalchemy.testing.plugin.pytestplugin import *
from sqlalchemy.testing.plugin.pytestplugin import (
    pytest_sessionfinish as _pytest_sessionfinish,
)
from sqlalchemy.testing.plugin.pytestplugin import (
    pytest_sessionstart as _pytest_sessionstart,
)

_TEST_SCHEMA = "TEST"


@contextmanager
def _pyexasol_connection(dsn="localhost:8563", user="SYS", password="exasol"):
    connection = pyexasol.connect(
        dsn=dsn,
        user=user,
        password=password,
        websocket_sslopt={"cert_reqs": ssl.CERT_NONE},
    )
    yield connection
    connection.close()


def pytest_sessionstart(session):
    with _pyexasol_connection() as con:
        con.execute(f"DROP SCHEMA IF EXISTS {_TEST_SCHEMA} CASCADE;")
        con.execute(f"CREATE SCHEMA {_TEST_SCHEMA};")
        con.commit()

    _pytest_sessionstart(session)


def pytest_sessionfinish(session):
    with _pyexasol_connection() as con:
        con.execute(f"DROP SCHEMA IF EXISTS {_TEST_SCHEMA} CASCADE;")
        con.commit()

    _pytest_sessionfinish(session)
