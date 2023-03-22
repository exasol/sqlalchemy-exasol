import pytest

from exasol.driver.websocket import connect


@pytest.fixture
def connection(exasol_config):
    config = exasol_config
    _connection = connect(
        dsn=f"{config.host}:{config.port}",
        username=config.username,
        password=config.password,
    )
    yield _connection
    _connection.close()
