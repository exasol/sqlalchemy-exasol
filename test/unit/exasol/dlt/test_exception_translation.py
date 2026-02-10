import pytest
from pyexasol.exceptions import (
    ExaAuthError,
    ExaCommunicationError,
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
    # pyexasol exceptions may access connection options in __str__/helpers
    options = {"dsn": "dummy", "user": "dummy", "verbose_error": False}

    def current_schema(self):
        return "DUMMY"

    def session_id(self):
        return "0"


def make_pyexasol_exception(exc_type):
    conn = DummyConnection()

    if exc_type is ExaQueryError:
        return ExaQueryError(conn, "SELECT 1", 1, "pyexasol boom")

    if exc_type is ExaAuthError:
        # ExaAuthError inherits ExaRequestError signature
        return ExaAuthError(conn, 1, "pyexasol boom")

    if exc_type is ExaRequestError:
        return ExaRequestError(conn, 1, "pyexasol boom")

    if exc_type is ExaCommunicationError:
        return ExaCommunicationError(conn, "pyexasol boom")

    if exc_type is ExaRuntimeError:
        return ExaRuntimeError(conn, "pyexasol boom")

    if exc_type is ExaError:
        return ExaError(conn, "pyexasol boom")

    raise AssertionError(f"Unhandled exception type in test: {exc_type!r}")


@pytest.mark.parametrize(
    "exc_type,expected_sa_exc",
    (
        (ExaQueryError, sa_exc.ProgrammingError),
        (ExaAuthError, sa_exc.OperationalError),
        (ExaRequestError, sa_exc.OperationalError),
        (ExaCommunicationError, sa_exc.OperationalError),
        (ExaRuntimeError, sa_exc.DatabaseError),
        (ExaError, sa_exc.DatabaseError),
    ),
)
def test_do_execute_translates_pyexasol_errors(exc_type, expected_sa_exc):
    pyexasol_exc = make_pyexasol_exception(exc_type)
    dialect = EXADialect()
    cursor = DummyCursor(pyexasol_exc)

    with pytest.raises(expected_sa_exc) as excinfo:
        dialect.do_execute(cursor, "SELECT 1", {"foo": "bar"})

    assert excinfo.value.__cause__ is pyexasol_exc
    assert excinfo.value.statement == "SELECT 1"
    assert excinfo.value.params == {"foo": "bar"}


def test_do_execute_propagates_unmapped_exceptions():
    dialect = EXADialect()
    original_exc = RuntimeError("unexpected")
    cursor = DummyCursor(original_exc)

    with pytest.raises(RuntimeError) as excinfo:
        dialect.do_execute(cursor, "SELECT 1", {})

    assert excinfo.value is original_exc
