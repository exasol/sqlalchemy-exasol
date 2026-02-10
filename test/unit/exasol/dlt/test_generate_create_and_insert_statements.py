import re
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

from sqlalchemy_exasol import base
from sqlalchemy_exasol.base import EXATimestamp


def _norm(sql: str) -> str:
    """Normalize SQL for stable string comparison."""
    return re.sub(r"\s+", " ", sql).strip()


def _dialect():
    return base.EXADialect()


def test_datetime_is_wrapped_to_exatimestamp_via_type_descriptor():
    dialect = _dialect()
    impl = DateTime().dialect_impl(dialect)

    # DateTime must be wrapped so values serialize correctly for PyExasol
    assert isinstance(impl, EXATimestamp)


def test_exatypecompiler_renders_wrapped_datetime_as_timestamp():
    dialect = _dialect()
    type_compiler = base.EXATypeCompiler(dialect)

    impl = DateTime().dialect_impl(dialect)
    assert type_compiler.process(impl) == "TIMESTAMP"


def test_create_table_and_insert_cover_many_types_as_compiled_strings():
    dialect = _dialect()
    metadata = MetaData()

    table = Table(
        "T_ALL_TYPES",
        metadata,
        Column("C_INT", Integer),
        Column("C_SMALLINT", SmallInteger),
        Column("C_BOOL", Boolean),
        Column("C_DATE", Date),
        Column("C_TIME", Time),
        Column("C_DATETIME", DateTime),  # wrapped -> EXATimestamp
        Column("C_VARCHAR_10", String(10)),
        Column("C_TEXT", Text),
        Column("C_NUMERIC", Numeric(19, 0)),
        Column("C_FLOAT", Float),
    )

    # --- CREATE TABLE ----------------------------------------------------
    create_sql = str(CreateTable(table).compile(dialect=dialect))

    expected_create = _norm(
        """
        CREATE TABLE "T_ALL_TYPES" (
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
        """
    )

    assert _norm(create_sql) == expected_create

    # --- INSERT ----------------------------------------------------------
    insert_sql = str(
        insert(table)
        .values(
            C_INT=1,
            C_SMALLINT=2,
            C_BOOL=True,
            C_DATE=date(2026, 1, 28),
            # Your dialect maps TIME to TIMESTAMP, but SQLAlchemy Time literals
            # will still be created from a `datetime.time` object. The compiler
            # may render it as '12:34:56' or coerce into a timestamp literal;
            # we lock to whatever your dialect emits.
            C_TIME=time(12, 34, 56),
            C_DATETIME=datetime(2026, 1, 28, 12, 34, 56),
            C_VARCHAR_10="hello",
            C_TEXT="world",
            C_NUMERIC=Decimal("123"),
            C_FLOAT=1.25,
        )
        .compile(dialect=dialect, compile_kwargs={"literal_binds": True})
    )

    # This expected form matches your dialect’s quoting behavior.
    # If TIME renders as something other than '12:34:56', update just that token.
    expected_insert = _norm(
        """
        INSERT INTO "T_ALL_TYPES"
        ("C_INT", "C_SMALLINT", "C_BOOL", "C_DATE", "C_TIME", "C_DATETIME",
         "C_VARCHAR_10", "C_TEXT", "C_NUMERIC", "C_FLOAT")
        VALUES
        (1, 2, true, '2026-01-28', '12:34:56', '2026-01-28 12:34:56',
         'hello', 'world', 123, 1.25)
        """
    )

    assert _norm(insert_sql) == expected_insert
