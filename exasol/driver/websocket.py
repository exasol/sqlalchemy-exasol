"""
This module provides a `PEP-249`_ compliant DBAPI interface, for a websocket based
database driver (see also `exasol-websocket-api`_).

.. _PEP-249: https://peps.python.org/pep-0249/#interfaceerror
.. _exasol-websocket-api: https://github.com/exasol/websocket-api
"""
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
from typing import (
    Optional,
    Protocol,
)

import pyexasol

apilevel = "2.0"  # pylint: disable=C0103
threadsafety = 1  # pylint: disable=C0103
paramstyle = "qmark"  # pylint: disable=C0103


class Warning(Exception):  # pylint: disable=W0622
    """
    Exception raised for important warnings like data truncations while inserting, etc.
    """


class Error(Exception):
    """
    Exception that is the base class of all other error exceptions.
    You can use this to catch all errors with one single except statement.
    Warnings are not considered errors and thus should not use this class as base.
    """


class InterfaceError(Error):
    """
    Exception raised for errors that are related to the database interface rather than
    the database itself.
    """


class DatabaseError(Error):
    """Exception raised for errors that are related to the database."""


class DataError(DatabaseError):
    """
    Exception raised for errors that are due to problems with the processed
    data like division by zero, numeric value out of range, etc.
    """


class OperationalError(DatabaseError):
    """
    Exception raised for errors that are related to the database’s operation
    and not necessarily under the control of the programmer, e.g. an unexpected
    disconnect occurs, the data source name is not found, a transaction
    could not be processed, a memory allocation error occurred during processing, etc.
    """


class IntegrityError(DatabaseError):
    """
    Exception raised when the relational integrity of the database is affected,
    e.g. a foreign key check fails.
    """


class InternalError(DatabaseError):
    """
    Exception raised when the database encounters an internal error,
    e.g. the cursor is not valid anymore, the transaction is out of sync, etc.
    """


class ProgrammingError(DatabaseError):
    """
    Exception raised for programming errors, e.g. table not found or already exists,
    syntax error in the SQL statement, wrong number of parameters specified, etc.
    """


class NotSupportedError(DatabaseError):
    """
    Exception raised in case a method or database API was used which is not supported
    by the database, e.g. requesting a .rollback() on a connection that does not
    support transaction or has transactions turned off.
    """


class Connection(Protocol):
    """
    Defines a connection protocol based on `connection-objects`_.

    .. connection-objects: https://peps.python.org/pep-0249/#connection-objects
    """

    def connect(self):
        """
        Connect to the database.

        Attention:
            Addition not required by pep-249.
        """

    def close(self):
        """
        Close the connection now (rather than whenever .__del__() is called).

        The connection will be unusable from this point forward; an Error (or subclass)
        exception will be raised if any operation is attempted with the connection.
        The same applies to all cursor objects trying to use the connection.
        Note that closing a connection without committing the changes first will cause
        an implicit rollback to be performed.
        """

    def commit(self):
        """
        Commit any pending transaction to the database.

        Note:
            If the database supports an auto-commit feature, this must be initially off.
            An interface method may be provided to turn it back on. Database modules
            that do not support transactions should implement this method with
            void functionality.
        """

    def rollback(self):
        """
        This method is optional since not all databases provide transaction support.

        In case a database does provide transactions this method causes the database
        to roll back to the start of any pending transaction. Closing a connection
        without committing the changes first will cause an implicit rollback
        to be performed.
        """

    def cursor(self):
        """
        Return a new Cursor Object using the connection.

        If the database does not provide a direct cursor concept, the module will have
        to emulate cursors using other means to the extent needed
        by this specification.
        """


class Cursor(Protocol):
    """
    Defines a protocol which is compliant with `cursor-objects`_.

    .. cursor-objects: https://peps.python.org/pep-0249/#cursor-objects
    """

    @property
    def arraysize(self):
        """
        This read/write attribute specifies the number of rows to fetch
        at a time with .fetchmany().

        It defaults to 1 meaning to fetch a single row at a time.
        Implementations must observe this value with respect to the .fetchmany() method,
        but are free to interact with the database a single row at a time.
        It may also be used in the implementation of .executemany().
        """

    @property
    def description(self):
        """
        This read-only attribute is a sequence of 7-item sequences.

        Each of these sequences contains information describing one result column:

            * name
            * type_code
            * display_size
            * internal_size
            * precision
            * scale
            * null_ok

        The first two items (name and type_code) are mandatory, the other five
        are optional and are set to None if no meaningful values can be provided.

        This attribute will be None for operations that do not return rows or if
        the cursor has not had an operation invoked via the .execute*() method yet.
        """

    @property
    def rowcount(self):
        """
        This read-only attribute specifies the number of rows that the last .execute*()
        produced (for DQL statements like SELECT) or affected(for DML statements
        like UPDATE or INSERT).

        The attribute is -1 in case no .execute*() has been performed on the cursor or
        the rowcount of the last operation is cannot be determined by the interface.

        .. note::

            Future versions of the DB API specification could redefine the latter case
            to have the object return None instead of -1.
        """

    def callproc(self, procname, *args, **kwargs):
        """
        Call a stored database procedure with the given name.
        (This method is optional since not all databases provide stored procedures)

        The sequence of parameters must contain one entry for each argument that the
        procedure expects. The result of the call is returned as modified copy of
        the input sequence. Input parameters are left untouched, output and
        input/output parameters replaced with possibly new values.

        The procedure may also provide a result set as output. This must then be
        made available through the standard .fetch*() methods.
        """

    def close(self):
        """
        Close the cursor now (rather than whenever __del__ is called).

        The cursor will be unusable from this point forward; an Error (or subclass)
        exception will be raised if any operation is attempted with the cursor.
        """

    def execute(self, operation, *args, **kwargs):
        """
        Prepare and execute a database operation (query or command).

        Parameters may be provided as sequence or mapping and will be bound to
        variables in the operation. Variables are specified in a database-specific
        notation (see the module’s paramstyle attribute for details).

        A reference to the operation will be retained by the cursor.
        If the same operation object is passed in again, then the cursor can optimize
        its behavior. This is most effective for algorithms where the same operation
        is used, but different parameters are bound to it (many times).

        For maximum efficiency when reusing an operation, it is best to usethe
        .setinputsizes() method to specify the parameter types and sizes ahead of time.
        It is legal for a parameter to not match the predefined information;
        the implementation should compensate, possibly with a loss of efficiency.

        The parameters may also be specified as list of tuples to e.g. insert multiple
        rows in a single operation, but this kind of usage is deprecated: .executemany()
        should be used instead.

        Return values are not defined.
        """

    def executemany(self, operation, seq_of_parameters):
        """
        Prepare a database operation (query or command) and then execute it against all
        parameter sequences or mappings found in the sequence seq_of_parameters.

        Modules are free to implement this method using multiple calls to the .execute()
        method or by using array operations to have the database process the sequence
        as a whole in one call.

        Use of this method for an operation which produces one or more result sets
        constitutes undefined behavior, and the implementation is permitted
        (but not required) to raise an exception when it detects that a result set
        has been created by an invocation of the operation.

        The same comments as for .execute() also apply accordingly to this method.

        Return values are not defined.
        """

    def fetchone(self):
        """
        Fetch the next row of a query result set, returning a single sequence, or None
        when no more data is available.

        An Error (or subclass) exception is raised if the previous call to .execute*()
        did not produce any result set or no call was issued yet.
        """

    def fetchmany(self, size=None):
        """
        Fetch the next set of rows of a query result, returning a sequence of sequences
        (e.g. a list of tuples).

        An empty sequence is returned when no more rows are available. The number of
        rows to fetch per call is specified by the parameter. If it is not given,
        the cursor’s arraysize determines the number of rows to be fetched. The method
        should try to fetch as many rows as indicated by the size parameter.
        If this is not possible due to the specified number of rows not being available,
        fewer rows may be returned.

        An Error (or subclass) exception is raised if the previous call to .execute*()
        did not produce any result set or no call was issued yet.

        Note there are performance considerations involved with the size parameter.
        For optimal performance, it is usually best to use the .arraysize attribute.
        If the size parameter is used, then it is best for it to retain the same value
        from one .fetchmany() call to the next.
        """

    def fetchall(self):
        """
        Fetch all (remaining) rows of a query result, returning them as a sequence of
        sequences (e.g. a list of tuples).

        Note that the cursor’s arraysize attribute can affect the performance of this
        operation. An Error (or subclass) exception is raised if the previous call to
        .execute*() did not produce any result set or no call was issued yet.
        """

    def nextset(self):
        """
        This method will make the cursor skip to the next available set, discarding any
        remaining rows from the current set.
        (This method is optional since not all databases support multiple result sets)

        If there are no more sets, the method returns None. Otherwise, it returns a true
        value and subsequent calls to the .fetch*() methods will return rows from the
        next result set.

        An Error (or subclass) exception is raised if the previous call to .execute*()
        did not produce any result set or no call was issued yet.
        """

    def setinputsizes(self, sizes):
        """
        This can be used before a call to .execute*() to predefine memory areas for the
        operation’s parameters.

        sizes is specified as a sequence — one item for each input parameter. The item
        should be a Type Object that corresponds to the input that will be used, or it
        should be an integer specifying the maximum length of a string parameter. If the
        item is None, then no predefined memory area will be reserved for that column
        (this is useful to avoid predefined areas for large inputs).

        This method would be used before the .execute*() method is invoked.

        Implementations are free to have this method do nothing and users are free
        to not use it.
        """

    def setoutputsizes(self, size, column):
        """
        Set a column buffer size for fetches of large columns (e.g. LONGs, BLOBs, etc.).

        The column is specified as an index into the result sequence. Not specifying
        the column will set the default size for all large columns in the cursor.
        This method would be used before the .execute*() method is invoked.

        Implementations are free to have this method do nothing and users are free
        to not use it.
        """


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
    def callproc(self, procname, *args, **kwargs):
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
    def execute(self, operation, *args, **kwargs):
        """See also :py:meth: `Cursor.execute`"""
        connection = self._connection.connection
        self._cursor = connection.execute(operation, *args, **kwargs)

    @_is_not_closed
    def executemany(self, operation, seq_of_parameters):
        """See also :py:meth: `Cursor.executemany`"""
        connection = self._connection.connection
        self._cursor = connection.cls_statement(connection, operation, prepare=True)
        self._cursor.execute_prepared(seq_of_parameters)

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
