import pyexasol
from packaging.version import Version
from pyexasol.data_types.websocket_types import WebSocketDataType
from sqlalchemy import text

from examples.config import (
    DEFAULT_SCHEMA_NAME,
    ENGINE,
    SQL_ALCHEMY,
)

if Version(pyexasol.__version__) < Version("3.0.0"):
    raise RuntimeError("This demo won't work with PyExasol versions older than 3.0.0.")

TABLE_NAME = "PYEXASOL_DBAPI_TYPE_CONVERSION"
FULL_TABLE_NAME = f"{DEFAULT_SCHEMA_NAME}.{TABLE_NAME}"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
DATA_TYPE_COLUMNS = (
    ("BOOLEAN_VALUE", "BOOLEAN"),
    ("CHAR_VALUE", "CHAR(5)"),
    ("DATE_VALUE", "DATE"),
    ("DECIMAL_FRACTION", "DECIMAL(18, 3)"),
    ("DECIMAL_INTEGER", "DECIMAL(18, 0)"),
    ("DOUBLE_VALUE", "DOUBLE"),
    ("GEOMETRY_VALUE", "GEOMETRY"),
    ("HASHTYPE_VALUE", "HASHTYPE(16 BYTE)"),
    ("INTERVAL_DAY_SECOND", "INTERVAL DAY(9) TO SECOND(6)"),
    ("INTERVAL_YEAR_MONTH", "INTERVAL YEAR(4) TO MONTH"),
    ("TIMESTAMP_LOCAL_VALUE", "TIMESTAMP WITH LOCAL TIME ZONE"),
    ("TIMESTAMP_VALUE", "TIMESTAMP(6)"),
    ("VARCHAR_VALUE", "VARCHAR(20)"),
)
EXASOL_TYPES = tuple(data_type for _, data_type in DATA_TYPE_COLUMNS)
CREATE_TABLE = f"""
CREATE TABLE IF NOT EXISTS {FULL_TABLE_NAME} (
    BOOLEAN_VALUE BOOLEAN,
    CHAR_VALUE CHAR(5),
    DATE_VALUE DATE,
    DECIMAL_FRACTION DECIMAL(18, 3),
    DECIMAL_INTEGER DECIMAL(18, 0),
    DOUBLE_VALUE DOUBLE,
    GEOMETRY_VALUE GEOMETRY,
    HASHTYPE_VALUE HASHTYPE(16 BYTE),
    INTERVAL_DAY_SECOND INTERVAL DAY(9) TO SECOND(6),
    INTERVAL_YEAR_MONTH INTERVAL YEAR(4) TO MONTH,
    TIMESTAMP_LOCAL_VALUE TIMESTAMP WITH LOCAL TIME ZONE,
    TIMESTAMP_VALUE TIMESTAMP(6),
    VARCHAR_VALUE VARCHAR(20)
)
"""
INSERT_ROW = f"""
INSERT INTO {FULL_TABLE_NAME} (
    BOOLEAN_VALUE,
    CHAR_VALUE,
    DATE_VALUE,
    DECIMAL_FRACTION,
    DECIMAL_INTEGER,
    DOUBLE_VALUE,
    GEOMETRY_VALUE,
    HASHTYPE_VALUE,
    INTERVAL_DAY_SECOND,
    INTERVAL_YEAR_MONTH,
    TIMESTAMP_LOCAL_VALUE,
    TIMESTAMP_VALUE,
    VARCHAR_VALUE
)
VALUES (
    TRUE,
    'xy',
    DATE '2026-09-11',
    42.125,
    42,
    42.5,
    'LINESTRING (10 20, 30 40)',
    '6ba7b8109dad11d180b400c04fd430c8',
    INTERVAL '3 04:05:06.654' DAY TO SECOND,
    INTERVAL '1-11' YEAR TO MONTH,
    TIMESTAMP '2026-09-11 12:34:56.123456',
    TIMESTAMP '2026-09-11 12:34:56.123456',
    'example'
)
"""


def custom_fetch_mapper(value, data_type):
    """Convert VARCHAR values to uppercase and leave other values unchanged."""
    if value is None:
        return None
    if data_type["type"] == WebSocketDataType.String.value:
        return value.upper()
    return value


def fetch_one_row(engine):
    """Fetch one row through SQLAlchemy."""
    with engine.connect() as connection:
        return connection.execute(text(f"SELECT * FROM {FULL_TABLE_NAME}")).fetchone()


def ensure_demo_table(engine):
    """Create and seed the demonstration table when it is not already populated."""
    SQL_ALCHEMY.create_schema(engine=engine, schema=DEFAULT_SCHEMA_NAME)
    with engine.begin() as connection:
        connection.execute(text(CREATE_TABLE))
        connection.execute(text(INSERT_ROW))


def print_comparison(default_row, custom_row):
    """Print default and custom DBAPI values side by side."""
    rows = [
        (data_type, repr(default_value), repr(custom_value))
        for data_type, default_value, custom_value in zip(
            EXASOL_TYPES, default_row, custom_row
        )
    ]
    type_width, default_width, custom_width = (
        max(map(len, column_values)) for column_values in zip(*rows)
    )
    rows_equal = default_row == custom_row
    comparison = "output is equal" if rows_equal else "output is not equal"

    print(
        f"{YELLOW}Rows equal: {rows_equal} "
        f"({comparison} between the default and custom mapper){RESET}"
    )
    print(
        f"\n{'Exasol type':<{type_width}} | "
        f"{BLUE}{'PyExasol default mapper':<{default_width}}{RESET} | "
        f"{GREEN}{'Custom mapper':<{custom_width}}{RESET}"
    )
    print(f"{'-' * type_width}-+-{'-' * default_width}-+-{'-' * custom_width}")
    for data_type, default_value, custom_value in rows:
        print(
            f"{data_type:<{type_width}} | "
            f"{BLUE}{default_value:<{default_width}}{RESET} | "
            f"{GREEN}{custom_value:<{custom_width}}{RESET}"
        )


default_engine = ENGINE
custom_engine = SQL_ALCHEMY.create_engine(
    connect_args={"fetch_mapper": custom_fetch_mapper},
)

ensure_demo_table(default_engine)
default_row = fetch_one_row(default_engine)
custom_row = fetch_one_row(custom_engine)
print_comparison(default_row, custom_row)
