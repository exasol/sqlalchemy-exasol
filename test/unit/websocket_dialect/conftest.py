from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine


@pytest.fixture(
    params=[
        pytest.param("exa", id="exa-driver"),
        pytest.param("exa+websocket", id="websocket-driver"),
    ]
)
def uninitialized_engine(request, monkeypatch):
    """Create an engine whose dialect initialization cannot query a server.

    ``pyexasol.connect`` is mocked by the tests. Pooling, pre-ping, and DBAPI
    connection/cursor behavior remain real.
    """
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
def mock_connection_factory():
    """Return a factory for fresh minimal PyExasol connection mocks."""

    def create_mock_connection():
        connection = Mock(is_closed=False)
        connection.options = {"verbose_error": False}
        return connection

    return create_mock_connection
