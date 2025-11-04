import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

from sqlalchemy_exasol.version import VERSION
from sqlalchemy_exasol.websocket import EXADialect_websocket


@pytest.mark.parametrize(
    "url,expected_kwargs",
    [
        (
            make_url("exa+websocket://localhost:8888"),
            {
                "dsn": "localhost:8888",
                "tls": True,
                "certificate_validation": True,
                "client_name": "EXASOL:SQLA:WS",
                "client_version": VERSION,
            },
        ),
        (
            make_url("exa+websocket://sys:exasol@localhost:8888"),
            {
                "dsn": "localhost:8888",
                "password": "exasol",
                "username": "sys",
                "tls": True,
                "certificate_validation": True,
                "client_name": "EXASOL:SQLA:WS",
                "client_version": VERSION,
            },
        ),
        (
            make_url(
                "exa+websocket://sys:exasol@localhost:8888/TEST?"
                "CONNECTIONCALL=en_US.UTF-8&DRIVER=EXAODBC"
                "&SSLCertificate=SSL_VERIFY_NONE"
            ),
            {
                "dsn": "localhost:8888",
                "password": "exasol",
                "username": "sys",
                "tls": True,
                "certificate_validation": False,
                "schema": "TEST",
                "client_name": "EXASOL:SQLA:WS",
                "client_version": VERSION,
            },
        ),
        (
            make_url(
                "exa+websocket://sys:exasol@localhost:8888/TEST?"
                "CONNECTIONCALL=en_US.UTF-8&DRIVER=EXAODBC"
                "&SSLCertificate=SSL_VERIFY_NONE"
                "&ENCRYPTION=N"
            ),
            {
                "dsn": "localhost:8888",
                "password": "exasol",
                "username": "sys",
                "tls": False,
                "certificate_validation": False,
                "schema": "TEST",
                "client_name": "EXASOL:SQLA:WS",
                "client_version": VERSION,
            },
        ),
    ],
)
def test_create_connection_args(url, expected_kwargs):
    dialect = EXADialect_websocket()
    actual = dialect.create_connect_args(url)

    actual_args, actual_kwargs = actual

    assert actual_args == []
    assert actual_kwargs == expected_kwargs


def test_raises_an_exception_for_invalid_arguments():
    url = make_url(
        "exa+websocket://sys:exasol@localhost:8888/TEST?"
        "CONNECTIONCALL=en_US.UTF-8&DRIVER=EXAODBC"
        "&ENCRYPTION=N"
    )

    dialect = EXADialect_websocket()

    with pytest.raises(ArgumentError) as exec_info:
        _, _ = dialect.create_connect_args(url)

    expected = "Certificate validation (True), can't be used without TLS (False)."
    actual = f"{exec_info.value}"
    assert actual == expected
