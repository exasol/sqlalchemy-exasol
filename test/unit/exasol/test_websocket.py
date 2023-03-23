import pytest
from sqlalchemy.engine import make_url

from sqlalchemy_exasol.websocket import EXADialect_websocket


@pytest.mark.parametrize(
    "url,expected",
    [
        (
            make_url("exa+websocket://localhost:8888"),
            ([], {"dsn": "localhost:8888"}),
        ),
        (
            make_url("exa+websocket://sys:exasol@localhost:8888"),
            ([], {"dsn": "localhost:8888", "password": "exasol", "username": "sys"}),
        ),
        (
            make_url(
                "exa+websocket://sys:exasol@localhost:8888/TEST?"
                "CONNECTIONCALL=en_US.UTF-8&DRIVER=EXAODBC"
                "&SSLCertificate=SSL_VERIFY_NONE"
            ),
            (
                [],
                {
                    "dsn": "localhost:8888",
                    "password": "exasol",
                    "username": "sys",
                    "tls": False,
                    "schema": "TEST",
                },
            ),
        ),
    ],
)
def test_create_connection_args(url, expected):
    dialect = EXADialect_websocket()
    actual = dialect.create_connect_args(url)

    actual_args, actual_kwargs = actual
    expected_args, expected_kwargs = expected

    assert actual_args == expected_args
    assert actual_kwargs == expected_kwargs
