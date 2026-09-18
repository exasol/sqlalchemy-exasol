from unittest.mock import Mock

import pyexasol
import pytest
from sqlalchemy import create_engine


@pytest.fixture(
    params=[
        pytest.param("exa", id="exa-driver"),
        pytest.param("exa+websocket", id="websocket-driver"),
    ]
)
def uninitialized_engine(request, monkeypatch):
    """Create an engine whose dialect initialization cannot query a server."""
    engine = create_engine(
        f"{request.param}://localhost:8563",
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )
    monkeypatch.setattr(engine.dialect, "initialize", lambda connection: None)
    yield engine
    engine.dispose()


@pytest.fixture
def mock_pyexasol_connection(monkeypatch):
    server = Mock(is_closed=False)
    server.options = {"verbose_error": False}
    connect = Mock(return_value=server)
    monkeypatch.setattr(pyexasol, "connect", connect)
    return server
