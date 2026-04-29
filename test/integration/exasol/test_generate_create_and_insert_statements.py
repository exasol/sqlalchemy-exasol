import re
import uuid
from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    MetaData,
    Numeric,
    SmallInteger,
    String,
    Table,
    Text,
    Time,
    insert,
)
from sqlalchemy.schema import CreateTable
from sqlalchemy.testing import (
    config,
    fixtures,
)


def _norm(sql: str) -> str:
    return re.sub(r"\s+", " ", sql).strip()


class GenerateCreateAndInsertStatementsTest(fixtures.TablesTest):
    __backend__ = True

    def test_create_table_and_insert_cover_many_types_as_compiled_strings_and_execute(
        self,
    ):
        metadata = MetaData()
        table_name = f'T_ALL_TYPES_{uuid.uuid4().hex[:8].upper()}'

        table = Table(
            table_name,
            metadata,
            Column("C_INT", Integer),
            Column("C_SMALLINT", SmallInteger),
            Column("C_BOOL", Boolean),
            Column("C_DATE", Date),
            Column("C_TIME", Time),
            Column("C_DATETIME", DateTime),
            Column("C_VARCHAR_10", String(10)),
            Column("C_TEXT", Text),
            Column("C_NUMERIC", Numeric(19, 0)),
            Column("C_FLOAT", Float),
        )

        create_sql = str(CreateTable(table).compile(dialect=config.db.dialect))
        expected_create = _norm(
            f'''
            CREATE TABLE "{table_name}" (
                "C_INT" INTEGER,
                "C_SMALLINT" SMALLINT,
                "C_BOOL" BOOLEAN,
                "C_DATE" DATE,
                "C_TIME" VARCHAR(16),
                "C_DATETIME" TIMESTAMP,
                "C_VARCHAR_10" VARCHAR(10),
                "C_TEXT" VARCHAR(2000000),
                "C_NUMERIC" NUMERIC(19, 0),
                "C_FLOAT" FLOAT
            )
            '''
        )
        assert _norm(create_sql) == expected_create

        insert_sql = str(
            insert(table)
            .values(
                C_INT=1,
                C_SMALLINT=2,
                C_BOOL=True,
                C_DATE=date(2026, 1, 28),
                C_TIME=time(12, 34, 56),
                C_DATETIME=datetime(2026, 1, 28, 12, 34, 56),
                C_VARCHAR_10="hello",
                C_TEXT="world",
                C_NUMERIC=Decimal("123"),
                C_FLOAT=1.25,
            )
            .compile(
                dialect=config.db.dialect,
                compile_kwargs={"literal_binds": True},
            )
        )

        expected_insert = _norm(
            f'''
            INSERT INTO "{table_name}"
            ("C_INT", "C_SMALLINT", "C_BOOL", "C_DATE", "C_TIME", "C_DATETIME",
             "C_VARCHAR_10", "C_TEXT", "C_NUMERIC", "C_FLOAT")
            VALUES
            (1, 2, true, '2026-01-28', '12:34:56', '2026-01-28 12:34:56',
             'hello', 'world', 123, 1.25)
            '''
        )
        assert _norm(insert_sql) == expected_insert

        with config.db.connect() as conn:
            try:
                conn.exec_driver_sql(create_sql)
                conn.exec_driver_sql(insert_sql)
                result = conn.exec_driver_sql(
                    f'SELECT COUNT(*) FROM "{table_name}"'
                ).scalar_one()
                assert result == 1
            finally:
                conn.exec_driver_sql(f'DROP TABLE IF EXISTS "{table_name}"')
