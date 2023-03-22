import pyexasol
import pytest


@pytest.fixture
def control_connection(exasol_config):
    """
    Returns a db connection which can be used to interact with the test database.
    """
    config = exasol_config
    connection = pyexasol.connect(
        dsn=f"{config.host}:{config.port}",
        user=config.username,
        password=config.password,
    )
    yield connection
    connection.close()
