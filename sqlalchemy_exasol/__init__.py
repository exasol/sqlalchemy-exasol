
from sqlalchemy_exasol import base, pyodbc

# default dialect
base.dialect = pyodbc.dialect

__all__ = (
    'BLOB', 'BOOLEAN', 'CHAR', 'DATE', 'DATETIME', 'DECIMAL', 'FLOAT', 'INTEGER',
    'NUMERIC', 'SMALLINT', 'TEXT', 'TIME', 'TIMESTAMP', 'VARCHAR', 'dialect', 'REAL'
)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
