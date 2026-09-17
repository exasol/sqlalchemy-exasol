"""Regression contracts for both registered websocket aliases; no database needed."""

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
from sqlalchemy.exc import DBAPIError


def _mock_connection():
    """Return a minimal PyExasol connection mock for dialect tests."""
    connection = Mock(is_closed=False)
    connection.options = {"verbose_error": False}
    return connection


def test_first_checkout_recovers_after_communication_error(engine, monkeypatch):
    stale, fresh = _mock_connection(), _mock_connection()
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
    server = _mock_connection()
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


def test_direct_dbapi_communication_cause_is_disconnect(engine):
    error = dbapi2.Error()
    error.__cause__ = ExaCommunicationError(_mock_connection(), "socket closed")

    assert engine.dialect.is_disconnect(error, None, None)


def test_in_flight_failure_is_not_replayed(engine, monkeypatch):
    server = _mock_connection()
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


class TestDisconnectCause:
    def test_non_dbapi_error_with_communication_cause_is_not_disconnect(self, engine):
        error = ValueError()
        error.__cause__ = ExaCommunicationError(_mock_connection(), "socket closed")

        assert not engine.dialect.is_disconnect(error, None, None)

    def test_indirect_communication_cause_is_not_disconnect(self, engine):
        intermediate = ValueError()
        intermediate.__cause__ = ExaCommunicationError(
            _mock_connection(), "socket closed"
        )
        error = dbapi2.Error()
        error.__cause__ = intermediate

        assert not engine.dialect.is_disconnect(error, None, None)

    def test_context_only_communication_cause_is_not_disconnect(self, engine):
        error = dbapi2.Error()
        error.__context__ = ExaCommunicationError(_mock_connection(), "socket closed")

        assert not engine.dialect.is_disconnect(error, None, None)
