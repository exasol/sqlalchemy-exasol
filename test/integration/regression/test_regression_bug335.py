import pytest
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
    sql,
)
from sqlalchemy.sql.ddl import (
    CreateSchema,
    DropSchema,
)


@pytest.fixture
def connection_string(exasol_config):
    config = exasol_config
    return (
        f"exa+websocket://{config.username}:{config.password}@{config.host}:{config.port}/"
        f"?DEFAULTPARAMSIZE=200&INTTYPESINRESULTSIFPOSSIBLE=y"
        "&FINGERPRINT=NOCERTCHECK&CONNECTIONLCALL=en_US.UTF-8&AUTOCOMMIT=0"
    )


@pytest.fixture()
def test_schema(pyexasol_connection):
    connection = pyexasol_connection
    schema = "REGRESSION_335"
    connection.execute(CreateSchema(schema))
    connection.commit()
    yield schema
    connection.execute(DropSchema(schema, cascade=True))
    connection.commit()


@pytest.fixture()
def users_table(pyexasol_connection, test_schema):
    connection = pyexasol_connection
    table_name = "users"
    connection.execute(
        sql.text(
            f"create table {test_schema}.{table_name} (id DECIMAL(18) identity primary key, name VARCHAR(2000) UTF8)"
        )
    )
    connection.commit()
    yield test_schema, table_name


def test_lastrowid_does_not_create_extra_commit(
    exasol_config, users_table, connection_string
):
    """
    For further details on this regression see `Issue-335 <https://github.com/exasol/sqlalchemy-exasol/issues/335>`_.
    """
    schema_name, table_name = users_table
    metadata = MetaData()
    engine = create_engine(connection_string)

    table = Table(
        table_name,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(2000)),
        schema=schema_name,
    )

    with engine.connect() as connection:
        with connection.begin() as transaction:
            # Insert without an explicit ID will trigger a call to `get_lastrowid`
            # which in turn cause the unintended autocommit
            insert_statement = insert(table).values(name="Gandalf")
            connection.execute(insert_statement)
            transaction.rollback()

        result = connection.execute(
            sql.text(f"SELECT * FROM {schema_name}.{table_name};")
        ).fetchall()
    assert len(result) == 0
