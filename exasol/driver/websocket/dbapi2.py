"""
This module provides a `PEP-249`_ compliant DBAPI interface, for a websocket based
database driver (see also `exasol-websocket-api`_).

.. _PEP-249: https://peps.python.org/pep-0249/#interfaceerror
.. _exasol-websocket-api: https://github.com/exasol/websocket-api
"""
import decimal
from collections import defaultdict
from dataclasses import (
    astuple,
    dataclass,
)
from datetime import (
    date,
    datetime,
    time,
)
from enum import (
    IntFlag,
    auto,
)
from functools import wraps
from time import localtime
from typing import Optional

from exasol.driver.websocket._errors import (
    DatabaseError,
    DataError,
    Error,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    Warning,
)
from exasol.driver.websocket._protocols import (
    Connection,
    Cursor,
)

apilevel = "2.0"  # pylint: disable=C0103
threadsafety = 1  # pylint: disable=C0103
paramstyle = "qmark"  # pylint: disable=C0103

__all__ = [
    # constants
    "apilevel",
    "threadsafety",
    "paramstyle",
    # errors
    "Warning",
    "Error",
    "InterfaceError",
    "DatabaseError",
    "DataError",
    "OperationalError",
    "InternalError",
    "IntegrityError",
    "InternalError",
    "ProgrammingError",
    "NotSupportedError",
    # protocols
    "Connection",
    "Cursor",
]

import pyexasol


def Date(year: int, month: int, day: int) -> date:  # pylint: disable=C0103
    """This function constructs an object holding a date value."""
    return date(year, month, day)


def Time(hour: int, minute: int, second: int) -> time:  # pylint: disable=C0103
    """This function constructs an object holding a time value."""
    return time(hour, minute, second)


def Timestamp(  # pylint: disable=C0103
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> datetime:
    """This function constructs an object holding a time stamp value."""
    return datetime(year, month, day, hour, minute, second)


def DateFromTicks(ticks: int) -> date:  # pylint: disable=C0103
    """
    This function constructs an object holding a date value from the given ticks value
    (number of seconds since the epoch; see the documentation of the standard
    Python time module for details).
    """
    year, month, day = localtime(ticks)[:3]
    return Date(year, month, day)


def TimeFromTicks(ticks: int) -> time:  # pylint: disable=C0103
    """
    This function constructs an object holding a time value from the given ticks value
    (number of seconds since the epoch; see the documentation of the standard
    Python time module for details).
    """
    hour, minute, second = localtime(ticks)[3:6]
    return Time(hour, minute, second)


def TimestampFromTicks(ticks: int) -> datetime:  # pylint: disable=C0103
    """
    This function constructs an object holding a time stamp value from the
    given ticks value (number of seconds since the epoch; see the documentation
    of the standard Python time module for details).
    """
    year, month, day, hour, minute, second = localtime(ticks)[:6]
    return Timestamp(year, month, day, hour, minute, second)


class Types(IntFlag):
    """
    This enum defines the supported DBAPI2 types.

    Types:
        STRING type
            This type object is used to describe columns in a database
            that are string-based (e.g. CHAR).
        BINARY type
            This type object is used to describe (long) binary columns in a database
            (e.g. LONG, RAW, BLOBs).
        NUMBER type
            This type object is used to describe numeric columns in a database.
        DATETIME type
            This type object is used to describe date/time columns in a database.
        ROWID type
            This type object is used to describe the “Row ID” column in a database.
    """

    STRING = auto()
    BINARY = auto()
    NUMBER = auto()
    DATETIME = auto()
    ROWID = auto()


STRING = Types.STRING
STRING = Types.BINARY
NUMBER = Types.NUMBER
DATETIME = Types.DATETIME
ROWID = Types.ROWID


@dataclass
class MetaData:
    """Meta data describing a result column"""

    name: str
    type_code: Types
    display_size: Optional[int] = None
    internal_size: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    null_ok: Optional[bool] = None


def _from_pyexasol(name, metadata) -> MetaData:
    type_mapping = defaultdict(
        lambda: Types.STRING, {"DOUBLE": Types.NUMBER, "DECIMAL": Types.NUMBER}
    )
    key_mapping = {
        "name": "name",
        "type_code": "type",
        "precision": "precision",
        "scale": "scale",
        "display_size": "unknown",
        "internal_size": "size",
        "null_ok": "unknown",
    }
    metadata = defaultdict(lambda: None, metadata)
    metadata["type"] = type_mapping[metadata["type"]]
    metadata["name"] = name
    return MetaData(**{k: metadata[v] for k, v in key_mapping.items()})


def _requires_connection(method):
    """
    Decorator requires the object to have a working connection.

    Raises:
        Error if the connection object has no active connection.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self._connection:
            raise Error("No active connection available")
        return method(self, *args, **kwargs)

    return wrapper


class DefaultConnection:
    """
    Implementation of a websocket based connection.

    For more details see :class: `Connection` protocol definition.
    """

    def __init__(
        self,
        dsn: str = None,
        username: str = None,
        password: str = None,
        schema: str = "",
        autocommit: bool = True,
        tls: bool = True,
    ):
        """
        Create a DefaultConnection object.

        Args:

            dsn: Connection string, same format as standard JDBC/ODBC drivers.
            username: which will be used for the authentication.
            password: which will be used for the authentication
            schema: to open after connecting.
            autocommit: enable autocommit.
            tls: enable tls.
        """

        # for more details see pyexasol.connection.ExaConnection
        self._options = {
            "dsn": dsn,
            "user": username,
            "password": password,
            "schema": schema,
            "autocommit": autocommit,
            "snapshot_transactions": None,
            "connection_timeout": 10,
            "socket_timeout": 30,
            "query_timeout": 0,
            "compression": False,
            "encryption": tls,
            "fetch_dict": False,
            "fetch_mapper": None,
            "fetch_size_bytes": 5 * 1024 * 1024,
            "lower_ident": False,
            "quote_ident": False,
            "json_lib": "json",
            "verbose_error": True,
            "debug": False,
            "debug_logdir": None,
            "udf_output_bind_address": None,
            "udf_output_connect_address": None,
            "udf_output_dir": None,
            "http_proxy": None,
            "client_name": None,
            "client_version": None,
            "client_os_username": None,
            "protocol_version": 3,
            "websocket_sslopt": None,
            "access_token": None,
            "refresh_token": None,
        }
        self._connection = None

    def connect(self):
        """See also :py:meth: `Connection.connect`"""
        try:
            self._connection = pyexasol.connect(**self._options)
        except pyexasol.exceptions.ExaConnectionError as ex:
            raise Error("Connection failed") from ex
        except Exception as ex:
            raise Error() from ex
        return self

    @property
    def connection(self):
        """Underlying connection used by this DefaultConnection"""
        return self._connection

    def close(self):
        """See also :py:meth: `Connection.close`"""
        if not self._connection:
            return
        try:
            self._connection.close()
        except Exception as ex:
            raise Error() from ex

    @_requires_connection
    def commit(self):
        """See also :py:meth: `Connection.commit`"""
        try:
            self._connection.commit()
        except Exception as ex:
            raise Error() from ex

    @_requires_connection
    def rollback(self):
        """See also :py:meth: `Connection.rollback`"""
        try:
            self._connection.rollback()
        except Exception as ex:
            raise Error() from ex

    @_requires_connection
    def cursor(self):
        """See also :py:meth: `Connection.cursor`"""
        return DefaultCursor(self)

    def __del__(self):
        self.close()


def _requires_result(method):
    """
    Decorator requires the object to have a result.

    Raises:
        Error if the cursor object has not produced a result yet.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self._cursor:
            raise Error("No result has been produced.")
        return method(self, *args, **kwargs)

    return wrapper


def _is_not_closed(method):
    """
    Decorator requires the object to have a result.

    Raises:
        Error if the cursor object has not produced a result yet.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self._is_closed:
            raise Error("Cursor is closed, further operations are not permitted.")
        return method(self, *args, **kwargs)

    return wrapper


class DefaultCursor:
    """
    Implementation of a cursor based on the DefaultConnection.

    For more details see :class: `Cursor` protocol definition.
    """

    # see https://peps.python.org/pep-0249/#arraysize
    DBAPI_DEFAULT_ARRAY_SIZE = 1

    def __init__(self, connection):
        self._connection = connection
        self._cursor = None
        self._is_closed = False

    @property
    @_is_not_closed
    def arraysize(self):
        """See also :py:meth: `Cursor.arraysize`"""
        return self.DBAPI_DEFAULT_ARRAY_SIZE

    @property
    @_is_not_closed
    def description(self):
        """See also :py:meth: `Cursor.description`"""
        if not self._cursor:
            return None
        columns_metadata = (
            _from_pyexasol(name, metadata)
            for name, metadata in self._cursor.columns().items()
        )
        columns_metadata = [astuple(metadata) for metadata in columns_metadata]
        return columns_metadata

    @property
    @_is_not_closed
    def rowcount(self):
        """
        See also :py:meth: `Cursor.rowcount`

        Attention: This implementation of the rowcount attribute deviates slightly
                   from what the dbapi2 requires.

               Difference:

                    If the rowcount of the last operation cannot be determined it will
                    return 0.

                    Expected by DBAPI2 = -1
                    Actually returned  = 0
        """
        if not self._cursor:
            return -1
        return self._cursor.rowcount()

    @_is_not_closed
    def callproc(self, procname, parameters=None):
        """See also :py:meth: `Cursor.callproc`"""
        raise NotSupportedError("Optional and therefore not supported")

    @_is_not_closed
    def close(self):
        """See also :py:meth: `Cursor.close`"""
        self._is_closed = True
        if not self._cursor:
            return
        self._cursor.close()

    @_is_not_closed
    def execute(self, operation, parameters=None):
        """See also :py:meth: `Cursor.execute`"""
        connection = self._connection.connection

        if parameters:
            self.executemany(operation, [parameters])
            return

        self._cursor = connection.execute(operation)

    @_is_not_closed
    def executemany(self, operation, seq_of_parameters):
        """See also :py:meth: `Cursor.executemany`"""
        parameters = [
            [str(p) if isinstance(p, (decimal.Decimal, float)) else p for p in params]
            for params in seq_of_parameters
        ]
        connection = self._connection.connection
        self._cursor = connection.cls_statement(connection, operation, prepare=True)
        self._cursor.execute_prepared(parameters)

    @_requires_result
    @_is_not_closed
    def fetchone(self):
        """See also :py:meth: `Cursor.fetchone`"""
        return self._cursor.fetchone()

    @_requires_result
    @_is_not_closed
    def fetchmany(self, size=None):
        """See also :py:meth: `Cursor.fetchmany`"""
        size = size if size is not None else self.arraysize
        return self._cursor.fetchmany(size)

    @_requires_result
    @_is_not_closed
    def fetchall(self):
        """See also :py:meth: `Cursor.fetchall`"""
        return self._cursor.fetchall()

    @_is_not_closed
    def nextset(self):
        """See also :py:meth: `Cursor.nextset`"""
        raise NotSupportedError("Optional and therefore not supported")

    @_is_not_closed
    def setinputsizes(self, sizes):
        """See also :py:meth: `Cursor.setinputsizes`

        Attention:
            This method does nothing.
        """

    @_is_not_closed
    def setoutputsize(self, size, column):
        """See also :py:meth: `Cursor.setoutputsize`

        Attention:
            This method does nothing.
        """

    def __del__(self):
        if self._is_closed:
            return
        self.close()


def connect(connection_class=DefaultConnection, **kwargs) -> Connection:
    """
    Creates a connection to the database.

    Args:
        connection_class: which shall be used to construct a connection object.
        kwargs: compatible with the provided connection_class.

    Returns:

        returns a dbapi2 complaint connection object.
    """
    connection = connection_class(**kwargs)
    return connection.connect()
