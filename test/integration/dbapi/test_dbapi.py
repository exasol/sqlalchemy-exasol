from inspect import cleandoc

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


@pytest.mark.parametrize(
    "sql_statement", ["SELECT 1;", "SELECT * FROM VALUES BETWEEN 1 AND 15 WITH STEP 4;"]
)
def test_cursor_execute(cursor, sql_statement):
    # Because the dbapi does not specify a required return value, this is just a smoke test
    # to ensure the execute call won't crash.
    cursor.execute(sql_statement)


def _id_func(value):
    if not isinstance(value, str):
        return ""
    return value


@pytest.mark.parametrize(
    "sql_statement, expected",
    [
        ("SELECT 1;", (1,)),
        ("SELECT * FROM VALUES (1, 2, 3);", (1, 2, 3)),
        ("SELECT * FROM VALUES BETWEEN 1 AND 15 WITH STEP 4;", (1,)),
    ],
    ids=str,
)
def test_cursor_fetchone(cursor, sql_statement, expected):
    cursor.execute(sql_statement)
    assert cursor.fetchone() == expected


@pytest.mark.parametrize("method", ("fetchone", "fetchmany", "fetchall"))
def test_cursor_function_raises_exception_if_no_result_have_been_produced(
    cursor, method
):
    expected = "No result have been produced."
    cursor_method = getattr(cursor, method)
    with pytest.raises(Error) as e_info:
        cursor_method()
    assert f"{e_info.value}" == expected


@pytest.mark.parametrize(
    "sql_statement, size, expected",
    [
        ("SELECT 1;", None, [(1,)]),
        ("SELECT 1;", 1, [(1,)]),
        ("SELECT 1;", 10, [(1,)]),
        ("SELECT * FROM VALUES ((1,2), (3,4), (5,6));", None, [(1, 2)]),
        ("SELECT * FROM VALUES ((1,2), (3,4), (5,6));", 1, [(1, 2)]),
        ("SELECT * FROM VALUES ((1,2), (3,4), (5,6));", 2, [(1, 2), (3, 4)]),
        ("SELECT * FROM VALUES ((1,2), (3,4), (5,6));", 10, [(1, 2), (3, 4), (5, 6)]),
    ],
    ids=str,
)
def test_cursor_fetchmany(cursor, sql_statement, size, expected):
    cursor.execute(sql_statement)
    assert cursor.fetchmany(size) == expected


@pytest.mark.parametrize(
    "sql_statement, expected",
    [
        ("SELECT 1;", [(1,)]),
        ("SELECT * FROM VALUES ((1,2), (3,4));", [(1, 2), (3, 4)]),
        ("SELECT * FROM VALUES ((1,2), (3,4), (5,6));", [(1, 2), (3, 4), (5, 6)]),
        (
            "SELECT * FROM VALUES ((1,2), (3,4), (5,6), (7, 8));",
            [(1, 2), (3, 4), (5, 6), (7, 8)],
        ),
    ],
    ids=str,
)
def test_cursor_fetchmany(cursor, sql_statement, expected):
    cursor.execute(sql_statement)
    assert cursor.fetchall() == expected


def test_description_returns_none_if_no_query_have_been_executed(cursor):
    assert cursor.description is None


@pytest.mark.parametrize(
    "sql_statement, expected",
    [
        (
            "SELECT CAST(A as INT) A FROM VALUES 1, 2, 3 as T(A);",
            (("col_name", "NUMBER", None, None, None, None, None),),
        ),
        (
            "SELECT CAST(A as DOUBLE) A FROM VALUES 1, 2, 3 as T(A);",
            (("col_name", "NUMBER", None, None, None, None, None),),
        ),
        (
            "SELECT CAST(A as BOOL) A FROM VALUES TRUE, FALSE, TRUE as T(A);",
            (("col_name", "NUMBER", None, None, None, None, None),),
        ),
        (
            "SELECT CAST(A as VARCHAR(10)) A FROM VALUES 'Foo', 'Bar' as T(A);",
            (("col_name", "NUMBER", None, None, None, None, None),),
        ),
        (
            cleandoc(
                """
             SELECT CAST(A as INT) A, CAST(B as VARCHAR(100)) B, CAST(C as BOOL) C, CAST(D as DOUBLE) D
             FROM VALUES ((1,'Some String', TRUE, 1.0), (3,'Other String', FALSE, 2.0)) as TB(A, B, C, D);
            """
            ),
            (
                ("col_name", "STRING", None, None, None, None, None),
                ("col_name", "STRING", None, None, None, None, None),
            ),
        ),
    ],
    ids=str,
)
def test_description_attribute(cursor, sql_statement, expected):
    cursor.execute(sql_statement)
    assert cursor.description == expected
