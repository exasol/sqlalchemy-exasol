"""Unit tests for passing PyExasol DBAPI mapper options via ``connect_args``.

How the mappers convert values is covered by the integration tests, e.g. in
``test_insert_mapper.py``. These tests check that SQLAlchemy-Exasol hands the options
on to the DBAPI and document where the DBAPI keeps them.
"""

from unittest.mock import (
    Mock,
    call,
)

import pyexasol
import pytest
from exasol.driver.websocket import dbapi2
from sqlalchemy import create_engine

from test.helpers.pyexasol_versions import (
    requires_pyexasol_3,
    requires_pyexasol_4,
)


def fetch_mapper(value, data_type):
    return f"{value}-mapper"


def insert_mapper(value, data_type):
    return f"{value}-mapper"


@pytest.fixture
def server():
    """Mock of the PyExasol connection, so that no database is needed."""
    server = Mock(is_closed=False)
    server.options = {"verbose_error": False}
    return server


@pytest.fixture
def pyexasol_connect(server, monkeypatch):
    connect = Mock(return_value=server)
    monkeypatch.setattr(pyexasol, "connect", connect)
    return connect


@pytest.fixture(params=["exa", "exa+websocket"])
def create_test_engine(request, pyexasol_connect, monkeypatch):
    """
    Return a function creating an engine for the given ``connect_args``.

    The real DBAPI is used, but the dialect initialization is skipped and
    ``pyexasol.connect`` is mocked.
    """
    engines = []

    def create(connect_args):
        engine = create_engine(
            f"{request.param}://localhost:8563", connect_args=connect_args
        )
        engines.append(engine)
        monkeypatch.setattr(engine.dialect, "initialize", lambda connection: None)
        return engine

    yield create
    for engine in engines:
        engine.dispose()


@pytest.fixture
def open_connection(create_test_engine, pyexasol_connect):
    """
    Return a function opening a connection for the given ``connect_args``.

    The function returns the DBAPI connection and the ``pyexasol.connect`` mock.
    """

    def open_with(connect_args):
        with create_test_engine(connect_args).connect() as connection:
            return connection.connection.dbapi_connection, pyexasol_connect

    return open_with


def test_mappers_are_passed_to_the_dbapi(open_connection, monkeypatch):
    # Mock the DBAPI's connection factory: the options are not valid for every
    # PyExasol version, but SQLAlchemy-Exasol should pass them on regardless.
    dbapi_connect = Mock()
    monkeypatch.setattr(dbapi2, "connect", dbapi_connect)

    open_connection({"fetch_mapper": fetch_mapper, "insert_mapper": insert_mapper})

    kwargs = dbapi_connect.call_args.kwargs
    assert kwargs["fetch_mapper"] is fetch_mapper
    assert kwargs["insert_mapper"] is insert_mapper


@requires_pyexasol_3
def test_fetch_mapper_is_used_for_the_results(
    create_test_engine, pyexasol_connect, server
):
    recording_fetch_mapper = Mock(wraps=fetch_mapper)
    column_type = {"type": "VARCHAR"}
    statement = Mock()
    statement.columns.return_value = {"V": column_type}

    def fetchall():
        # PyExasol applies the fetch_mapper it was connected with to the raw values.
        mapper = pyexasol_connect.call_args.kwargs["fetch_mapper"]
        return [[mapper(value, column_type)] for value in ("a", "b")]

    statement.fetchall.side_effect = fetchall
    server.execute.return_value = statement
    engine = create_test_engine({"fetch_mapper": recording_fetch_mapper})

    with engine.connect() as connection:
        rows = connection.exec_driver_sql("SELECT V FROM T").fetchall()

    # The mapper receives each value with the column's metadata and its output
    # is what SQLAlchemy returns.
    assert recording_fetch_mapper.call_args_list == [
        call("a", column_type),
        call("b", column_type),
    ]
    assert [tuple(row) for row in rows] == [("a-mapper",), ("b-mapper",)]


@requires_pyexasol_4
def test_insert_mapper_is_used_for_the_parameters(create_test_engine, server):
    recording_insert_mapper = Mock(wraps=insert_mapper)
    statement = Mock()
    statement.parameter_data = {"columns": [{"dataType": {"type": "VARCHAR"}}]}
    statement.columns.return_value = {}
    statement.rowcount.return_value = 2
    server.cls_statement.return_value = statement
    engine = create_test_engine({"insert_mapper": recording_insert_mapper})

    with engine.begin() as connection:
        connection.exec_driver_sql("INSERT INTO t VALUES (?)", [("a",), ("b",)])

    # The mapper receives each value with the column's metadata and its output
    # is what the DBAPI sends to PyExasol.
    assert recording_insert_mapper.call_args_list == [
        call("a", {"type": "VARCHAR"}),
        call("b", {"type": "VARCHAR"}),
    ]
    statement.execute_prepared.assert_called_once_with([["a-mapper"], ["b-mapper"]])
