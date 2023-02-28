import pytest

from exasol.driver.websocket import (
    Error,
    connect,
)


def test_websocket_dbapi(exasol_test_config):
    cfg = exasol_test_config
    connection = connect(
        dsn=f"{cfg.host}:{cfg.port}", username=cfg.username, password=cfg.password
    )
    assert connection


def test_websocket_dbapi_connect_fails():
    dsn = "127.0.0.2:9999"
    username = "ShouldNotExist"
    password = "ThisShouldNotBeAValidPasswordForTheUser"
    with pytest.raises(Error) as e_info:
        connect(dsn=dsn, username=username, password=password)
    assert "Connection failed" == f"{e_info.value}"


def test_retrieve_cursor_via_websocket_dbapi(exasol_test_config):
    config = exasol_test_config
    connection = connect(
        dsn=f"{config.host}:{config.port}",
        username=config.username,
        password=config.password,
    )
    cursor = connection.cursor()
    assert cursor
    connection.close()


def test_retrieve_cursor_via_websocket_dbapi(exasol_test_config):
    config = exasol_test_config
    connection = connect(
        dsn=f"{config.host}:{config.port}",
        username=config.username,
        password=config.password,
    )
    cursor = connection.cursor()
    assert cursor
    cursor.close()
