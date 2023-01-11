"""
This module provides a `PEP-249 <https://peps.python.org/pep-0249/#interfaceerror>`_ compliant DBAPI interface,
for a `websocket based <https://github.com/exasol/websocket-api>`_ `EXASOL <https://www.exasol.com/de/>`_ database driver.
"""
from datetime import (
    date,
    datetime,
    time,
)
from enum import (
    IntFlag,
    auto,
)
from time import localtime
from typing import Protocol

apilevel = "2.0"
threadsafety = 1
paramstyle = "qmark"


class Warning(Exception):
    """Exception raised for important warnings like data truncations while inserting, etc."""


class Error(Exception):
    """
    Exception that is the base class of all other error exceptions.
    You can use this to catch all errors with one single except statement.
    Warnings are not considered errors and thus should not use this class as base.
    """


class InterfaceError(Error):
    """Exception raised for errors that are related to the database interface rather than the database itself."""


class DatabaseError(Error):
    """Exception raised for errors that are related to the database."""


class DataError(DatabaseError):
    """
    Exception raised for errors that are due to problems with the processed data like division by zero,
    numeric value out of range, etc."""


class OperationalError(DatabaseError):
    """
    Exception raised for errors that are related to the database’s operation
    and not necessarily under the control of the programmer, e.g. an unexpected disconnect occurs,
    the data source name is not found, a transaction could not be processed,
    a memory allocation error occurred during processing, etc.
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
    Exception raised in case a method or database API was used which is not supported by the database,
    e.g. requesting a .rollback() on a connection that does not support transaction
    or has transactions turned off.
    """


class Connection(Protocol):
    """
    Defines a protocol which is compliant with https://peps.python.org/pep-0249/#connection-objects connection objects.
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

        The connection will be unusable from this point forward;
        an Error (or subclass) exception will be raised if any operation is attempted with the connection.
        The same applies to all cursor objects trying to use the connection.
        Note that closing a connection without committing the changes first will cause an implicit rollback
        to be performed.
        """

    def commit(self):
        """
        Commit any pending transaction to the database.

        Note:
            If the database supports an auto-commit feature, this must be initially off.
            An interface method may be provided to turn it back on.
            Database modules that do not support transactions should implement this method with void functionality.
        """

    def rollback(self):
        """
        This method is optional since not all databases provide transaction support.

        In case a database does provide transactions this method causes the database to roll back to the start
        of any pending transaction. Closing a connection without committing the changes first
        will cause an implicit rollback to be performed.
        """

    def cursor(self):
        """
        Return a new Cursor Object using the connection.

        If the database does not provide a direct cursor concept, the module will have to emulate cursors
        using other means to the extent needed by this specification.
        """


class Cursor(Protocol):
    """
    Defines a protocol which is compliant with https://peps.python.org/pep-0249/#cursor-objects cursor objects.
    """

    @property
    def arraysize(self):
        ...

    @property
    def description(self):
        ...

    @property
    def rowcount(self):
        ...

    def callproc(self, procname, parameters):
        ...

    def close(self):
        ...

    def execute(self, operation, parameters):
        ...

    def executemany(self, operation, seq_of_parameters):
        ...

    def fetchone(self):
        ...

    def fetchmany(self, size=None):
        ...

    def fetchall(self):
        ...

    def nextset(self):
        ...

    def setinputsizes(self, sizes):
        ...

    def setoutputsizes(self, size, column):
        ...


def Date(year: int, month: int, day: int) -> date:
    return date(year, month, day)


def Time(hour: int, minute: int, second: int) -> time:
    return time(hour, minute, second)


def Timestamp(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> datetime:
    return datetime(year, month, day, hour, minute, second)


def DateFromTicks(ticks: int) -> date:
    year, month, day = localtime(ticks)[:3]
    return Date(year, month, day)


def TimeFromTicks(ticks: int) -> time:
    hour, minute, second = localtime(ticks)[3:6]
    return Time(hour, minute, second)


def TimestampFromTicks(ticks: int) -> datetime:
    year, month, day, hour, minute, second = localtime(ticks)[:6]
    return Timestamp(year, month, day, hour, minute, second)


class Types(IntFlag):
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


class DefaultConnection:
    def __init__(self, **kwargs):
        raise NotImplemented()

    def connect(self, **kwargs):
        raise NotImplemented()

    def close(self):
        raise NotImplemented()

    def commit(self):
        raise NotImplemented()

    def rollback(self):
        raise NotImplemented()

    def cursor(self):
        raise NotImplemented()

    def __del__(self):
        self.close()


class DefaultCursor:
    # see https://peps.python.org/pep-0249/#arraysize
    DBAPI_DEFAULT_ARRAY_SIZE = 1

    @property
    def arraysize(self):
        return self.DBAPI_DEFAULT_ARRAY_SIZE

    @property
    def description(self):
        raise NotImplemented()

    @property
    def rowcount(self):
        raise NotImplemented()

    def callproc(self, procname, parameters):
        raise NotImplemented()

    def close(self):
        raise NotImplemented()

    def execute(self, operation, parameters):
        raise NotImplemented()

    def executemany(self, operation, seq_of_parameters):
        raise NotImplemented()

    def fetchone(self):
        raise NotImplemented()

    def fetchmany(self, size=None):
        raise NotImplemented()

    def fetchall(self):
        raise NotImplemented()

    def nextset(self):
        raise NotSupportedError("Optional and therefore not supported")

    def setinputsizes(self, sizes):
        raise NotImplemented()

    def setoutputsizes(self, size, column):
        raise NotImplemented()

    def __del__(self):
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
    connection.connect()
    return connection
