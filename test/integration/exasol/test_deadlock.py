import time
from threading import Thread

import pytest
import sqlalchemy.testing as testing
from sqlalchemy import (
    create_engine,
    inspect,
)
from sqlalchemy.testing import (
    config,
    fixtures,
)


# TODO: get_schema_names, get_view_names and get_view_definition didn't cause deadlocks in this scenario
@pytest.mark.skipif(
    "pyodbc" not in str(testing.db.url),
    reason="We currently only support snapshot metadata requests in the pyodbc based dialect",
)
class MetadataTest(fixtures.TablesTest):
    __backend__ = True

    CONNECTION_ECHO = False
    WATCHDOG_ECHO = False

    def create_transaction(self, url, con_name):
        engine = create_engine(
            config.db.url, echo=self.CONNECTION_ECHO, logging_name="engine" + con_name
        )
        session = engine.connect().execution_options(autocommit=False)
        return engine, session

    def test_no_deadlock_for_get_table_names_without_fallback(self):
        def without_fallback(session2, schema, table):
            dialect = inspect(session2).dialect
            dialect.get_table_names(session2, schema=schema, use_sql_fallback=False)

        self.run_deadlock_for_table(without_fallback)

    # NOTE: If a DB >= 7.1.0 still deadlocks here, it may due to the usage of an old ODBC driver version
    @pytest.mark.skipif(
        testing.db.dialect.server_version_info >= (7, 1, 0),
        reason="DB version(s) after 7.1.0 should not deadlock here",
    )
    def test_deadlock_for_get_table_names_with_fallback(self):
        def with_fallback(session2, schema, table):
            dialect = inspect(session2).dialect
            dialect.get_table_names(session2, schema=schema, use_sql_fallback=True)

        with pytest.raises(Exception):
            self.run_deadlock_for_table(with_fallback)

    @pytest.mark.skipif(
        testing.db.dialect.server_version_info <= (7, 1, 0),
        reason="DB version(s) before 7.1.0 are expected to deadlock here",
    )
    def test_no_deadlock_for_get_table_names_with_fallback(self):
        def with_fallback(session2, schema, table):
            dialect = inspect(session2).dialect
            dialect.get_table_names(session2, schema=schema, use_sql_fallback=True)

        self.run_deadlock_for_table(with_fallback)

    def test_no_deadlock_for_get_columns_without_fallback(self):
        def without_fallback(session2, schema, table):
            dialect = inspect(session2).dialect
            dialect.get_columns(
                session2, schema=schema, table_name=table, use_sql_fallback=False
            )

        self.run_deadlock_for_table(without_fallback)

    def test_no_deadlock_for_get_columns_with_fallback(self):
        # TODO: Doesnt produce a deadlock anymore since last commit?
        def with_fallback(session2, schema, table):
            dialect = inspect(session2).dialect
            dialect.get_columns(
                session2, schema=schema, table_name=table, use_sql_fallback=True
            )

        self.run_deadlock_for_table(with_fallback)

    def test_no_deadlock_for_get_pk_constraint_without_fallback(self):
        def without_fallback(session2, schema, table):
            dialect = inspect(session2).dialect
            dialect.get_pk_constraint(
                session2, table_name=table, schema=schema, use_sql_fallback=False
            )

        self.run_deadlock_for_table(without_fallback)

    def test_no_deadlock_for_get_pk_constraint_with_fallback(self):
        def with_fallback(session2, schema, table):
            dialect = inspect(session2).dialect
            dialect.get_pk_constraint(
                session2, table_name=table, schema=schema, use_sql_fallback=True
            )

        self.run_deadlock_for_table(with_fallback)

    def test_no_deadlock_for_get_foreign_keys_without_fallback(self):
        def without_fallback(session2, schema, table):
            dialect = inspect(session2).dialect
            dialect.get_foreign_keys(
                session2, table_name=table, schema=schema, use_sql_fallback=False
            )

        self.run_deadlock_for_table(without_fallback)

    def test_no_deadlock_for_get_foreign_keys_with_fallback(self):
        def with_fallback(session2, schema, table):
            dialect = inspect(session2).dialect
            dialect.get_foreign_keys(
                session2, table_name=table, schema=schema, use_sql_fallback=True
            )

        self.run_deadlock_for_table(with_fallback)

    def test_no_deadlock_for_get_view_names_without_fallback(self):
        # TODO: think of other scenarios where metadata deadlocks with view could happen
        def without_fallback(session2, schema, table):
            dialect = inspect(session2).dialect
            dialect.get_view_names(
                session2, table_name=table, schema=schema, use_sql_fallback=False
            )

        self.run_deadlock_for_table(without_fallback)

    def test_no_deadlock_for_get_view_names_with_fallback(self):
        # TODO: think of other scenarios where metadata deadlocks with view could happen
        def with_fallback(session2, schema, table):
            dialect = inspect(session2).dialect
            dialect.get_view_names(
                session2, table_name=table, schema=schema, use_sql_fallback=True
            )

        self.run_deadlock_for_table(with_fallback)

    def watchdog(self, session0, schema):
        while self.watchdog_run:
            rs = session0.execute("SELECT * FROM SYS.EXA_ALL_SESSIONS")
            rs = [row for row in rs]
            if self.WATCHDOG_ECHO:
                print()
                print("===========================================")
                print("Watchdog")
                print("===========================================")
            for row in rs:
                if self.WATCHDOG_ECHO:
                    print(row)
                if row[7] is not None and "Waiting for" in row[7]:
                    if self.WATCHDOG_ECHO:
                        print(f"Killing session: {row[0]}")
                    session0.execute(f"kill session {row[0]}")
            if self.WATCHDOG_ECHO:
                print("===========================================")
                print()
            time.sleep(
                10
            )  # Only change with care, lower values might make tests unreliable

    def run_deadlock_for_table(self, function):
        c1 = config.db.connect()
        url = config.db.url

        schema = "deadlock_get_table_names_test_schema"
        engine0, session0 = self.create_transaction(url, "transaction0")
        try:
            session0.execute(f"DROP SCHEMA {schema} cascade")
        except:
            pass
        session0.execute(f"CREATE SCHEMA {schema}")
        session0.execute(
            f"CREATE OR REPLACE TABLE {schema}.deadlock_test1 (id int PRIMARY KEY)"
        )
        session0.execute(
            f"CREATE OR REPLACE TABLE {schema}.deadlock_test2 (id int PRIMARY KEY, fk int REFERENCES {schema}.deadlock_test1(id))"
        )
        session0.execute(f"INSERT INTO {schema}.deadlock_test1 VALUES 1")
        session0.execute(f"INSERT INTO {schema}.deadlock_test2 VALUES (1,1)")
        session0.execute("commit")
        self.watchdog_run = True
        t1 = Thread(target=self.watchdog, args=(session0, schema))
        t1.start()
        try:
            engine1, session1 = self.create_transaction(url, "transaction1")
            session1.execute("SELECT 1")

            session1.execute(f"SELECT * FROM {schema}.deadlock_test2")
            session1.execute(f"INSERT INTO {schema}.deadlock_test1 VALUES 2")

            engine3, session3 = self.create_transaction(url, "transaction3")
            session3.execute("SELECT 1")
            session3.execute(f"DELETE FROM {schema}.deadlock_test2 WHERE false")
            session3.execute("commit")

            engine2, session2 = self.create_transaction(url, "transaction2")
            session2.execute("SELECT 1")
            function(session2, schema, "deadlock_test2")

            session2.execute("commit")
            session1.execute("commit")
        except Exception as e:
            self.watchdog_run = False
            t1.join()
            raise e
        self.watchdog_run = False
        t1.join()

    def run_deadlock_for_get_view_names(self, function):
        c1 = config.db.connect()
        url = config.db.url

        schema = "deadlock_get_view_names_test_schema"
        engine0, session0 = self.create_transaction(url, "transaction0")
        try:
            session0.execute(f"DROP SCHEMA {schema} cascade")
        except:
            pass
        session0.execute(f"CREATE SCHEMA {schema}")
        session0.execute(
            f"CREATE OR REPLACE TABLE {schema}.deadlock_test_table (id int)"
        )
        session0.execute(
            f"CREATE OR REPLACE VIEW {schema}.deadlock_test_view_1 AS SELECT * FROM {schema}.deadlock_test_table"
        )
        session0.execute("commit")
        self.watchdog_run = True
        t1 = Thread(target=self.watchdog, args=(session0, schema))
        t1.start()
        try:
            engine1, session1 = self.create_transaction(url, "transaction1")
            session1.execute("SELECT 1")

            session1.execute(f"SELECT * FROM {schema}.deadlock_test_view_1")
            session1.execute(
                f"CREATE OR REPLACE VIEW {schema}.deadlock_test_view_2 AS SELECT * FROM {schema}.deadlock_test_table"
            )

            engine3, session3 = self.create_transaction(url, "transaction3")
            session3.execute("SELECT 1")
            session3.execute(f"DROP VIEW {schema}.deadlock_test_view_1")
            session3.execute("commit")

            engine2, session2 = self.create_transaction(url, "transaction2")
            session2.execute("SELECT 1")
            function(session2, schema)

            session2.execute("commit")
            session1.execute("commit")
        except Exception as e:
            self.watchdog_run = False
            t1.join()
            raise e
        self.watchdog_run = False
        t1.join()
