"""Regression contracts for both registered websocket aliases; no database needed."""

from unittest.mock import Mock

import pyexasol
import pytest
from exasol.driver.websocket import dbapi2
from pyexasol.exceptions import (
    ExaCommunicationError,
)
from sqlalchemy.exc import DBAPIError


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
