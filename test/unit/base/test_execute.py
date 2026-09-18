import pyexasol
import pytest
from exasol.driver.websocket import _errors as dbapi_exc
from packaging.version import Version
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
from sqlalchemy import text


class TestConnectionExecuteExceptions:
    @pytest.mark.parametrize(
        "exception_type,constructor_args,expected_sa_exception",
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
    def test_translates_legacy_pyexasol_errors(
        self,
        uninitialized_engine,
        mock_pyexasol_connection,
        exception_type,
        constructor_args,
        expected_sa_exception,
    ):
        """Test error translation kept for PyExasol versions older than 2.4.1.

        PyExasol version 2.4.1 and newer already perform this mapping in the
        DB-API layer. This can be removed when support for older versions is
        dropped. Tracked in https://github.com/exasol/sqlalchemy-exasol/issues/814.
        """
        server = mock_pyexasol_connection
        pyexasol_error = exception_type(server, *constructor_args, "unexpected error")
        server.execute.side_effect = pyexasol_error
        expected_exception = (
            expected_sa_exception
            if Version(pyexasol.__version__) >= Version("2.4.1")
            else sa_exc.DBAPIError
        )
        statement = text("SELECT 1")

        with uninitialized_engine.connect() as connection:
            with pytest.raises(expected_exception) as exception:
                connection.execute(statement)

        assert exception.value.__cause__.__cause__ is pyexasol_error

    @pytest.mark.parametrize(
        "exception_type,expected_sa_exception",
        (
            (dbapi_exc.Error, sa_exc.DBAPIError),
            (dbapi_exc.DatabaseError, sa_exc.DatabaseError),
            (dbapi_exc.DataError, sa_exc.DataError),
            (dbapi_exc.OperationalError, sa_exc.OperationalError),
            (dbapi_exc.IntegrityError, sa_exc.IntegrityError),
            (dbapi_exc.InternalError, sa_exc.InternalError),
            (dbapi_exc.ProgrammingError, sa_exc.ProgrammingError),
            (dbapi_exc.NotSupportedError, sa_exc.NotSupportedError),
            (dbapi_exc.InterfaceError, sa_exc.InterfaceError),
        ),
    )
    def test_translates_dbapi_errors(
        self,
        uninitialized_engine,
        mock_pyexasol_connection,
        exception_type,
        expected_sa_exception,
    ):
        """Test translation of exceptions raised by the DB-API layer."""
        server = mock_pyexasol_connection
        dbapi_error = exception_type("unexpected error")
        server.execute.side_effect = dbapi_error
        statement = text("SELECT 1")

        with uninitialized_engine.connect() as connection:
            with pytest.raises(expected_sa_exception) as exception:
                connection.execute(statement)

        assert exception.value.orig is dbapi_error
