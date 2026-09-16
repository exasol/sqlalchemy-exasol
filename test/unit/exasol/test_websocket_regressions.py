"""Regression contracts for both registered websocket aliases; no database needed."""

import datetime
import time
from unittest.mock import Mock

import pyexasol
import pytest
from exasol.driver.websocket import dbapi2
from pyexasol.exceptions import (
    ExaAuthError,
    ExaCommunicationError,
    ExaQueryAbortError,
    ExaQueryError,
    ExaQueryTimeoutError,
)
from sqlalchemy import (
    DateTime,
    create_engine,
)
from sqlalchemy.exc import DBAPIError


@pytest.fixture(
    params=[
        pytest.param("exa", id="exa-driver"),
        pytest.param("exa+websocket", id="websocket-driver"),
    ]
)
def engine(request, monkeypatch):
    engine = create_engine(
        f"{request.param}://localhost:8563",
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )
    # Server metadata is irrelevant to checkout. Keep real pool, ping, DBAPI and cursor.
    monkeypatch.setattr(engine.dialect, "initialize", lambda connection: None)
    yield engine
    engine.dispose()


@pytest.mark.parametrize(
    "text,expected",
    [
        pytest.param(
            "2026-09-11 12:34:56",
            datetime.datetime(2026, 9, 11, 12, 34, 56),
            id="no-fraction",
        ),
        pytest.param(
            "2026-09-11 12:34:56.1",
            datetime.datetime(2026, 9, 11, 12, 34, 56, 100000),
            id="one-digit-fraction-is-padded",
        ),
        pytest.param(
            "2026-09-11 12:34:56.123456",
            datetime.datetime(2026, 9, 11, 12, 34, 56, 123456),
            id="full-microsecond-precision",
        ),
        pytest.param(None, None, id="null-stays-null"),
        pytest.param(
            datetime.datetime(2026, 1, 1, 0, 0, 0, 123456),
            datetime.datetime(2026, 1, 1, 0, 0, 0, 123456),
            id="datetime-stays-unchanged",
        ),
    ],
)
def test_datetime_result(datetime_processor, text, expected):
    assert datetime_processor(text) == expected


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("invalid", id="not-a-datetime"),
        pytest.param("2024-02-30 00:00:00", id="invalid-calendar-date"),
        pytest.param("2026-09-11 12:34:56.1234567", id="too-many-fraction-digits"),
    ],
)
def test_datetime_invalid(datetime_processor, value):
    with pytest.raises(ValueError):
        datetime_processor(value)


@pytest.fixture
def datetime_processor(engine):
    return (
        DateTime().dialect_impl(engine.dialect).result_processor(engine.dialect, None)
    )


def test_datetime_is_not_interpreted_in_local_timezone(engine, monkeypatch):
    if not hasattr(time, "tzset"):
        pytest.skip("requires tzset")
    with monkeypatch.context() as timezone_patch:
        # A nonexistent local wall time must not be normalized through mktime.
        timezone_patch.setenv("TZ", "EST5EDT,M3.2.0,M11.1.0")
        time.tzset()
        try:
            processor = (
                DateTime()
                .dialect_impl(engine.dialect)
                .result_processor(engine.dialect, None)
            )
            assert processor("2026-03-08 02:30:00.123456") == datetime.datetime(
                2026, 3, 8, 2, 30, 0, 123456
            )
        finally:
            # tzset() reads TZ once; refresh it after monkeypatch restores TZ.
            timezone_patch.undo()
            time.tzset()


def transport():
    connection = Mock(is_closed=False)
    connection.options = {"verbose_error": False}
    return connection


def test_first_checkout_recovers_after_communication_error(engine, monkeypatch):
    stale, fresh = transport(), transport()
    connect = Mock(side_effect=[stale, fresh])
    monkeypatch.setattr(pyexasol, "connect", connect)
    with engine.connect() as connection:
        original = connection.connection.dbapi_connection
    stale.is_closed = True
    stale.execute.side_effect = ExaCommunicationError(stale, "socket closed")
    # Exactly one application checkout: no retry, dispose, or manual invalidation.
    with engine.connect() as connection:
        assert connection.connection.dbapi_connection is not original
        assert connection.connection.dbapi_connection.connection is fresh
    assert connect.call_count == 2
    stale.execute.assert_called_once_with("SELECT 1 FROM DUAL")


@pytest.mark.parametrize(
    "error_type",
    [
        pytest.param(ExaQueryError, id="query-error"),
        pytest.param(ExaAuthError, id="authentication-error"),
        pytest.param(ExaQueryTimeoutError, id="query-timeout"),
        pytest.param(ExaQueryAbortError, id="query-abort"),
    ],
)
def test_server_errors_are_not_disconnects(engine, monkeypatch, error_type):
    server = transport()
    connect = Mock(return_value=server)
    monkeypatch.setattr(pyexasol, "connect", connect)
    with engine.connect():
        pass
    cause = (
        error_type(server, "42000", "server rejected request")
        if error_type is ExaAuthError
        else error_type(server, "SELECT 1", "42000", "server rejected query")
    )
    server.execute.side_effect = cause
    with pytest.raises(DBAPIError) as caught:
        engine.connect()
    assert caught.value.orig.__cause__ is cause
    assert not caught.value.connection_invalidated
    assert connect.call_count == 1


def test_plain_dbapi_error_is_not_disconnect(engine):
    assert not engine.dialect.is_disconnect(dbapi2.Error("socket closed"), None, None)


def test_in_flight_failure_is_not_replayed(engine, monkeypatch):
    server = transport()
    connect = Mock(return_value=server)
    monkeypatch.setattr(pyexasol, "connect", connect)
    with engine.connect() as connection:
        server.is_closed = True
        server.execute.side_effect = ExaCommunicationError(server, "socket closed")
        with pytest.raises(DBAPIError) as caught:
            connection.exec_driver_sql("INSERT INTO T VALUES (1)")
        assert caught.value.connection_invalidated
        server.execute.assert_called_once_with("INSERT INTO T VALUES (1)")
        assert connect.call_count == 1


@pytest.mark.parametrize(
    "wrapper",
    [
        pytest.param("non_dbapi", id="non-dbapi-cause"),
        pytest.param("indirect", id="indirect-dbapi-cause"),
        pytest.param("context_only", id="context-only-cause"),
    ],
)
def test_only_direct_dbapi_communication_cause_is_disconnect(engine, wrapper):
    cause = ExaCommunicationError(transport(), "socket closed")
    error = dbapi2.Error()
    if wrapper == "non_dbapi":
        error = ValueError()
        error.__cause__ = cause
    elif wrapper == "indirect":
        intermediate = ValueError()
        intermediate.__cause__ = cause
        error.__cause__ = intermediate
    else:
        error.__context__ = cause
    assert not engine.dialect.is_disconnect(error, None, None)
