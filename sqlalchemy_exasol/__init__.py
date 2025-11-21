from sqlalchemy_exasol import (
    base,
    websocket,
)
from sqlalchemy_exasol.version import VERSION

__version__ = VERSION

# default dialect
base.dialect = websocket.dialect  # type: ignore

__all__ = (
    "BLOB",
    "BOOLEAN",
    "CHAR",
    "DATE",
    "DATETIME",
    "DECIMAL",
    "FLOAT",
    "INTEGER",
    "NUMERIC",
    "SMALLINT",
    "TEXT",
    "TIME",
    "TIMESTAMP",
    "VARCHAR",
    "dialect",
    "REAL",
)
