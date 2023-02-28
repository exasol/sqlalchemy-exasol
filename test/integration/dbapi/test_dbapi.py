import pytest

from exasol.driver.websocket import (
    Error,
    connect,
)


@pytest.fixture
def connection(exasol_test_config):
    config = exasol_test_config
    connection = connect(
        dsn=f"{config.host}:{config.port}",
        username=config.username,
        password=config.password,
    )
    yield connection
    connection.close()


@pytest.fixture
def cursor(connection):
    cursor = connection.cursor()
    yield cursor
    cursor.close()


def test_websocket_dbapi(exasol_test_config):
    cfg = exasol_test_config
    connection = connect(
        dsn=f"{cfg.host}:{cfg.port}", username=cfg.username, password=cfg.password
    )
    assert connection
    connection.close()


def test_websocket_dbapi_connect_fails():
    dsn = "127.0.0.2:9999"
    username = "ShouldNotExist"
    password = "ThisShouldNotBeAValidPasswordForTheUser"
    with pytest.raises(Error) as e_info:
        connect(dsn=dsn, username=username, password=password)
    assert "Connection failed" == f"{e_info.value}"


def test_retrieve_cursor_from_connection(connection):
    cursor = connection.cursor()
    assert cursor
    cursor.close()


def test_cursor_execute(cursor):
    # Because the dbapi does not specify a required return value, this is just a smoke test
    # to ensure the execute call won't crash.
    cursor.execute("SELECT 1;")


def test_cursor_fetchone(cursor):
    expected = (1,)
    cursor.execute("SELECT 1;")
    assert cursor.fetchone() == expected


def test_cursor_fetch_one_raises_exception_if_not_results_have_been_produced(cursor):
    expected = "No result have been produced."
    with pytest.raises(Error) as e_info:
        cursor.fetchone()
    assert f"{e_info.value}" == expected
