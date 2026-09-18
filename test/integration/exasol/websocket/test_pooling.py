"""Integration tests for websocket connection-pool behavior."""

import pyexasol
import pytest
import sqlalchemy as sa
from packaging.version import Version
from sqlalchemy.testing import fixtures


def current_session(connection):
    return connection.exec_driver_sql("SELECT CURRENT_SESSION").scalar_one()


def kill_session(admin_engine, session_id):
    with admin_engine.begin() as connection:
        connection.exec_driver_sql(f"KILL SESSION {int(session_id)}")


class TestConnectionPoolBehavior(fixtures.TestBase):
    def test_checkout_pooled_connection_recovers_after_communication_error(
        self, pooled_engine, admin_engine, schema
    ):
        # Setup: create committed data and return one connection to the pool.
        with pooled_engine.begin() as connection:
            connection.exec_driver_sql(f"CREATE TABLE {schema}.T (ID INT)")
            connection.exec_driver_sql(f"INSERT INTO {schema}.T VALUES (1)")
        with pooled_engine.connect() as connection:
            old_session = current_session(connection)

        # Action: kill the idle pooled session from an independent connection.
        kill_session(admin_engine, old_session)

        # Assert: the first checkout succeeds without application retry,
        # disposal, or manual invalidation, using a replacement session.
        with pooled_engine.connect() as connection:
            assert current_session(connection) != old_session
            assert (
                connection.exec_driver_sql(
                    f"SELECT COUNT(*) FROM {schema}.T"
                ).scalar_one()
                == 1
            )

    def test_disconnect_does_not_replay_uncommitted_write(
        self, pooled_engine, admin_engine, schema
    ):
        # Setup: create an empty table and begin an uncommitted transaction.
        with pooled_engine.begin() as connection:
            connection.exec_driver_sql(f"CREATE TABLE {schema}.T (ID INT)")

        # Action: Keep the test write separate so it remains uncommitted when the session
        # is killed; putting it in the begin() block above would commit it.
        with pooled_engine.connect() as connection:
            old_session = current_session(connection)
            connection.exec_driver_sql(f"INSERT INTO {schema}.T VALUES (1)")

            kill_session(admin_engine, old_session)

            # Assert: the failed write is reported and must not be replayed.
            with pytest.raises(sa.exc.DBAPIError) as caught:
                connection.exec_driver_sql(f"INSERT INTO {schema}.T VALUES (2)")
            assert caught.value.connection_invalidated

            # The lost transaction must be rolled back before the connection closes.
            connection.rollback()

        # Neither the original nor the failed write reached the table.
        with pooled_engine.connect() as connection:
            assert (
                connection.exec_driver_sql(
                    f"SELECT COUNT(*) FROM {schema}.T"
                ).scalar_one()
                == 0
            )

    # Compatibility path tracked in
    # https://github.com/exasol/sqlalchemy-exasol/issues/814.
    @pytest.mark.parametrize(
        "expected_exception",
        [
            (
                sa.exc.ProgrammingError
                if Version(pyexasol.__version__) >= Version("2.4.1")
                else sa.exc.DBAPIError
            )
        ],
    )
    def test_server_error_does_not_invalidate_healthy_connection(
        self, pooled_engine, schema, expected_exception
    ):
        # Setup: open a connection
        with pooled_engine.connect() as connection:
            old_session = current_session(connection)

            # Action: execute a query that the server rejects.
            with pytest.raises(expected_exception) as exception:
                connection.exec_driver_sql(f"SELECT * FROM {schema}.DOES_NOT_EXIST")

            # Assert: a server-side query error must not invalidate the connection.
            cause = exception.value.__cause__.__cause__
            assert f"object {schema}.DOES_NOT_EXIST not found" in str(cause)
            assert not exception.value.connection_invalidated
            # Clear the failed transaction before using the connection again.
            connection.rollback()
            # The same session remains usable.
            assert current_session(connection) == old_session
