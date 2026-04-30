from sqlalchemy_exasol import (
    base,
    websocket,
)
from sqlalchemy_exasol._metadata import __version__

# default dialect
base.dialect = websocket.dialect  # type: ignore

__all__ = (
    "__version__",
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
