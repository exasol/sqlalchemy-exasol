"""Regression contracts for both registered websocket aliases; no database needed."""

from unittest.mock import Mock

import pyexasol
import pytest
from pyexasol.exceptions import (
    ExaCommunicationError,
)
from sqlalchemy.exc import DBAPIError


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
