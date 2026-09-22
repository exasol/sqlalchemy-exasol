from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_connection_factory():
    """Return a factory for fresh minimal PyExasol connection mocks."""

    def create_mock_connection():
        connection = Mock(is_closed=False)
        connection.options = {"verbose_error": False}
        return connection

    return create_mock_connection
