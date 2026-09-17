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


def _create_query_error(server, error_type):
    return error_type(server, "SELECT 1", "42000", "server rejected query")


def _create_authentication_error(server, error_type):
    return error_type(server, "42000", "server rejected request")


def test_checkout_pooled_connection_recovers_after_communication_error(
    uninitialized_engine, mock_connection_factory, monkeypatch
):
    # Setup: populate the pool with a connection and prepare its replacement.
    old_connection = mock_connection_factory()
    new_connection = mock_connection_factory()
    connect = Mock(side_effect=[old_connection, new_connection])
    monkeypatch.setattr(pyexasol, "connect", connect)
    with uninitialized_engine.connect() as connection:
        original = connection.connection.dbapi_connection
    old_connection.is_closed = True
    old_connection.execute.side_effect = ExaCommunicationError(
        old_connection, "socket closed"
    )

    # Action: perform one application checkout after the pooled connection fails.
    with uninitialized_engine.connect() as connection:
        replacement = connection.connection.dbapi_connection

    # Assert: checkout recovers with the replacement without retry or manual invalidation.
    assert replacement is not original
    assert replacement.connection is new_connection
    assert connect.call_count == 2
    old_connection.execute.assert_called_once_with("SELECT 1 FROM DUAL")


@pytest.mark.parametrize(
    "error_type,exception_factory",
    [
        pytest.param(ExaQueryError, _create_query_error, id="query-error"),
        pytest.param(
            ExaAuthError, _create_authentication_error, id="authentication-error"
        ),
        pytest.param(ExaQueryTimeoutError, _create_query_error, id="query-timeout"),
        pytest.param(ExaQueryAbortError, _create_query_error, id="query-abort"),
    ],
)
def test_server_errors_are_not_disconnects(
    uninitialized_engine,
    mock_connection_factory,
    monkeypatch,
    error_type,
    exception_factory,
):
    # Setup: prepare a healthy connection that will return a server-side error.
    server = mock_connection_factory()
    connect = Mock(return_value=server)
    monkeypatch.setattr(pyexasol, "connect", connect)
    with uninitialized_engine.connect():
        pass
    cause = exception_factory(server, error_type)
    server.execute.side_effect = cause

    # Action: perform a checkout after the server rejects the pre-ping query.
    with pytest.raises(DBAPIError) as caught:
        uninitialized_engine.connect()

    # Assert: server errors do not invalidate a healthy pooled connection.
    assert caught.value.orig.__cause__ is cause
    assert not caught.value.connection_invalidated
    assert connect.call_count == 1


class TestIsDisconnect:
    def test_is_disconnect_for_direct_dbapi_communication_error(
        self, uninitialized_engine, mock_connection_factory
    ):
        error = dbapi2.Error()
        error.__cause__ = ExaCommunicationError(
            mock_connection_factory(), "socket closed"
        )

        is_disconnect = uninitialized_engine.dialect.is_disconnect(error, None, None)

        assert is_disconnect

    def test_is_not_disconnect_for_plain_dbapi_error(self, uninitialized_engine):
        error = dbapi2.Error("socket closed")

        is_disconnect = uninitialized_engine.dialect.is_disconnect(error, None, None)

        assert not is_disconnect

    def test_is_not_disconnect_for_non_dbapi_error_with_direct_communication_cause(
        self, uninitialized_engine, mock_connection_factory
    ):
        error = ValueError()
        error.__cause__ = ExaCommunicationError(
            mock_connection_factory(), "socket closed"
        )

        is_disconnect = uninitialized_engine.dialect.is_disconnect(error, None, None)

        assert not is_disconnect

    def test_is_not_disconnect_for_dbapi_error_with_indirect_communication_cause(
        self, uninitialized_engine, mock_connection_factory
    ):
        intermediate = ValueError()
        intermediate.__cause__ = ExaCommunicationError(
            mock_connection_factory(), "socket closed"
        )
        error = dbapi2.Error()
        error.__cause__ = intermediate

        is_disconnect = uninitialized_engine.dialect.is_disconnect(error, None, None)

        assert not is_disconnect

    def test_is_not_disconnect_for_dbapi_error_with_context_only_communication_cause(
        self, uninitialized_engine, mock_connection_factory
    ):
        error = dbapi2.Error()
        error.__context__ = ExaCommunicationError(
            mock_connection_factory(), "socket closed"
        )

        is_disconnect = uninitialized_engine.dialect.is_disconnect(error, None, None)

        assert not is_disconnect
