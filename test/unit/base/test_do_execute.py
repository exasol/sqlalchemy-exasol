import pytest
from exasol.driver.websocket import _errors as dbapi_exc
from pyexasol.exceptions import (
    ExaAuthError,
    ExaCommunicationError,
    ExaConcurrencyError,
    ExaConnectionError,
    ExaError,
    ExaQueryError,
    ExaRequestError,
    ExaRuntimeError,
)
from sqlalchemy import exc as sa_exc

from sqlalchemy_exasol.base import EXADialect


class DummyCursor:
    def __init__(self, exception_to_raise):
        self._exception_to_raise = exception_to_raise

    def execute(self, statement, parameters):
        raise self._exception_to_raise


class DummyConnection:
    # PyExasol exceptions may access connection options in __str__/helpers
    options = {"dsn": "dummy", "user": "dummy", "verbose_error": False}

    def current_schema(self):
        return "DUMMY"

    def session_id(self):
        return "0"


class TestDoExecuteException:
    """Test error translation kept for PyExasol versions older than 2.4.1.

    PyExasol version 2.4.1 and newer already perform this mapping in the
    DB-API layer. This can be removed when support for older versions is
    dropped. Tracked in https://github.com/exasol/sqlalchemy-exasol/issues/814.
    """

    @pytest.mark.parametrize(
        "exception_type,constructor_args,expected_sa_exc",
        (
            (ExaQueryError, ("SELECT 1", 1), sa_exc.ProgrammingError),
            (ExaAuthError, (1,), sa_exc.DatabaseError),
            (ExaRequestError, (1,), sa_exc.DatabaseError),
            (ExaConnectionError, (), sa_exc.OperationalError),
            (ExaCommunicationError, (), sa_exc.OperationalError),
            (ExaConcurrencyError, (), sa_exc.InterfaceError),
            (ExaRuntimeError, (), sa_exc.DatabaseError),
            (ExaError, (), sa_exc.DatabaseError),
        ),
    )
    def test_translates_pyexasol_errors(
        self, exception_type, constructor_args, expected_sa_exc
    ):
        connection = DummyConnection()
        pyexasol_exc = exception_type(connection, *constructor_args, "unexpected error")
        dialect = EXADialect()
        cursor = DummyCursor(pyexasol_exc)

        with pytest.raises(expected_sa_exc) as exception:
            dialect.do_execute(cursor, "SELECT 1", {"foo": "bar"})

        assert exception.value.__cause__ is pyexasol_exc
        assert exception.value.statement == "SELECT 1"
        assert exception.value.params == {"foo": "bar"}

    @pytest.mark.parametrize(
        "exception_type",
        [
            RuntimeError,
            dbapi_exc.Error,
            dbapi_exc.DatabaseError,
        ],
    )
    def test_propagates_unmapped_exceptions(self, exception_type):
        dialect = EXADialect()
        original_exc = exception_type("unexpected error")
        cursor = DummyCursor(original_exc)

        with pytest.raises(exception_type) as exception:
            dialect.do_execute(cursor, "SELECT 1", {})

        assert exception.value is original_exc
