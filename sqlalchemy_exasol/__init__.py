from sqlalchemy_exasol.version import VERSION
from sqlalchemy_exasol import base, pyodbc

__version__ = VERSION

# default dialect
base.dialect = pyodbc.dialect

__all__ = (
    'BLOB', 'BOOLEAN', 'CHAR', 'DATE', 'DATETIME', 'DECIMAL', 'FLOAT', 'INTEGER',
    'NUMERIC', 'SMALLINT', 'TEXT', 'TIME', 'TIMESTAMP', 'VARCHAR', 'dialect', 'REAL'
)
