try:
    from ._version import version as __version__
except ImportError:  # pragma: no cover
    __version__ = "unknown"

from sqlalchemy_exasol import base, pyodbc

# default dialect
base.dialect = pyodbc.dialect

__all__ = (
    'BLOB', 'BOOLEAN', 'CHAR', 'DATE', 'DATETIME', 'DECIMAL', 'FLOAT', 'INTEGER',
    'NUMERIC', 'SMALLINT', 'TEXT', 'TIME', 'TIMESTAMP', 'VARCHAR', 'dialect', 'REAL'
)
