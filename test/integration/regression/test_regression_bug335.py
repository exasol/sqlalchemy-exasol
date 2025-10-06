import warnings

import pytest
import sqlalchemy.exc
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
)

from exasol.odbc import (
    ODBC_DRIVER,
    odbcconfig,
)


@pytest.fixture
def pyodbc_connection_string(exasol_config):
    config = exasol_config
    return (
        f"exa+pyodbc://{config.username}:{config.password}@{config.host}:{config.port}/"
        f"?DEFAULTPARAMSIZE=200&INTTYPESINRESULTSIFPOSSIBLE=y"
        "&FINGERPRINT=NOCERTCHECK&CONNECTIONLCALL=en_US.UTF-8&driver=EXAODBC"
    )


@pytest.fixture()
def test_schema(pyexasol_connection):
    connection = pyexasol_connection
    schema = "REGRESSION_335"
    connection.execute(f"CREATE SCHEMA {schema}")
    connection.commit()
    yield schema
    connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
    connection.commit()


@pytest.fixture()
def users_table(pyexasol_connection, test_schema):
    connection = pyexasol_connection
    table_name = "users"
    connection.execute(
        f"create table {test_schema}.{table_name} (id DECIMAL(18) identity primary key, name VARCHAR(2000) UTF8)"
    )
    connection.commit()
    yield test_schema, table_name


def test_lastrowid_does_not_create_extra_commit(
    exasol_config, users_table, pyodbc_connection_string
):
    """
    For further details on this regression see `Issue-335 <https://github.com/exasol/sqlalchemy-exasol/issues/335>`_.
    """
    schema_name, table_name = users_table
    metadata = MetaData()
    engine = create_engine(pyodbc_connection_string)

    table = Table(
        table_name,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(2000)),
        schema=schema_name,
    )

    with odbcconfig(ODBC_DRIVER):
        conn = engine.connect()
        trans = conn.begin()

        # Insert without an explicit ID will trigger a call to `get_lastrowid`
        # which in turn cause the unintended autocommit
        insert_statement = insert(table).values(name="Gandalf")
        conn.execute(insert_statement)
        trans.rollback()

        result = conn.execute(
            f"SELECT * FROM {schema_name}.{table_name};"
        ).fetchall()
        conn.close()

        assert len(result) == 0
