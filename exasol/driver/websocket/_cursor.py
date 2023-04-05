"""
This module provides `PEP-249`_ DBAPI compliant cursor implementation.
(see also `PEP-249-cursor`_)

.. _PEP-249-cursor: https://peps.python.org/pep-0249/#cursor-objects
"""
import decimal
from collections import defaultdict
from dataclasses import (
    astuple,
    dataclass,
)
from functools import wraps
from typing import Optional

from exasol.driver.websocket._errors import (
    Error,
    NotSupportedError,
)
from exasol.driver.websocket._types import Types


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


class Cursor:
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
        if parameters:
            self.executemany(operation, [parameters])
            return

        connection = self._connection.connection
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
