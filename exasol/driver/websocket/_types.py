"""
This module provides `PEP-249`_ a DBAPI compliant types and type conversion definitions.
(see also `PEP-249-types`_)

.. _PEP-249-types: https://peps.python.org/pep-0249/#type-objects-and-constructors
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
BINARY = Types.BINARY
NUMBER = Types.NUMBER
DATETIME = Types.DATETIME
ROWID = Types.ROWID
