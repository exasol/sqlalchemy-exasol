# -*- coding: UTF-8 -*-

import time
from threading import Thread

import pytest
from sqlalchemy import create_engine
from sqlalchemy.testing import fixtures, config
import sqlalchemy.testing as testing
from sqlalchemy_exasol.base import EXADialect


#TODO get_schema_names, get_view_names and get_view_definition didn't cause deadlocks in this scenario
@pytest.mark.skipif("turbodbc" in str(testing.db.url), reason="We currently don't support snapshot metadata requests for turbodbc")
class MetadataTest(fixtures.TablesTest):
    __backend__ = True

    CONNECTION_ECHO = False
    WATCHDOG_ECHO = False

    def create_transaction(self, url, con_name):
        engine = create_engine(config.db.url, echo=self.CONNECTION_ECHO, logging_name="engine" + con_name)
        session = engine.connect().execution_options(autocommit=False)
        return engine, session

    def test_no_deadlock_for_get_table_names_without_fallback(self):
        def without_fallback(session2, schema, table):
            dialect = EXADialect()
            dialect.get_table_names(session2, schema=schema, use_sql_fallback=False)

        self.run_deadlock_for_table(without_fallback)

    def test_deadlock_for_get_table_names_with_fallback(self):
        def with_fallback(session2, schema, table):
            dialect = EXADialect()
            dialect.get_table_names(session2, schema=schema, use_sql_fallback=True)

        with pytest.raises(Exception):
            self.run_deadlock_for_table(with_fallback)
    
    def test_no_deadlock_for_get_columns_without_fallback(self):
        def without_fallback(session2, schema, table):
            dialect = EXADialect()
            dialect.get_columns(session2, schema=schema, table_name=table, use_sql_fallback=False)

        self.run_deadlock_for_table(without_fallback)

    def test_no_deadlock_for_get_columns_with_fallback(self):
        # TODO: Doesnt produce a deadlock anymore since last commit?
        def with_fallback(session2, schema, table):
            dialect = EXADialect()
            dialect.get_columns(session2, schema=schema, table_name=table, use_sql_fallback=True)

        self.run_deadlock_for_table(with_fallback)

    def test_no_deadlock_for_get_pk_constraint_without_fallback(self):
        def without_fallback(session2, schema, table):
            dialect = EXADialect()
            dialect.get_pk_constraint(session2, table_name=table, schema=schema, use_sql_fallback=False)

        self.run_deadlock_for_table(without_fallback)

    def test_deadlock_for_get_pk_constraint_with_fallback(self):
        def with_fallback(session2, schema, table):
            dialect = EXADialect()
            dialect.get_pk_constraint(session2, table_name=table, schema=schema, use_sql_fallback=True)

        with pytest.raises(Exception):
            self.run_deadlock_for_table(with_fallback)

    def test_no_deadlock_for_get_foreign_keys_without_fallback(self):
        def without_fallback(session2, schema, table):
            dialect = EXADialect()
            dialect.get_foreign_keys(session2, table_name=table, schema=schema, use_sql_fallback=False)

        self.run_deadlock_for_table(without_fallback)


    def test_deadlock_for_get_foreign_keys_with_fallback(self):
        def with_fallback(session2, schema, table):
            dialect = EXADialect()
            dialect.get_foreign_keys(session2, table_name=table, schema=schema, use_sql_fallback=True)

        with pytest.raises(Exception):
            self.run_deadlock_for_table(with_fallback)

    def test_no_deadlock_for_get_view_names_without_fallback(self):
        # TODO: think of other scenarios where metadata deadlocks with view could happen
        def without_fallback(session2, schema, table):
            dialect = EXADialect()
            dialect.get_view_names(session2, table_name=table, schema=schema, use_sql_fallback=False)

        self.run_deadlock_for_table(without_fallback)

    def test_no_deadlock_for_get_view_names_with_fallback(self):
        # TODO: think of other scenarios where metadata deadlocks with view could happen
        def with_fallback(session2, schema, table):
            dialect = EXADialect()
            dialect.get_view_names(session2, table_name=table, schema=schema, use_sql_fallback=True)

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
                        print("Killing session: %s" % row[0])
                    session0.execute("kill session %s" % row[0])
            if self.WATCHDOG_ECHO:
                print("===========================================")
                print()
            time.sleep(10) # Only change with care, lower values might make tests unreliable

    def run_deadlock_for_table(self, function):
        c1 = config.db.connect()
        url = config.db.url

        schema = "deadlock_get_table_names_test_schema"
        engine0, session0 = self.create_transaction(url, "transaction0")
        try:
            session0.execute("DROP SCHEMA %s cascade" % schema)
        except:
            pass
        session0.execute("CREATE SCHEMA %s" % schema)
        session0.execute("CREATE OR REPLACE TABLE %s.deadlock_test1 (id int PRIMARY KEY)" % schema)
        session0.execute(
            "CREATE OR REPLACE TABLE %s.deadlock_test2 (id int PRIMARY KEY, fk int REFERENCES %s.deadlock_test1(id))" % (
                schema, schema))
        session0.execute("INSERT INTO %s.deadlock_test1 VALUES 1" % schema)
        session0.execute("INSERT INTO %s.deadlock_test2 VALUES (1,1)" % schema)
        session0.execute("commit")
        self.watchdog_run = True
        t1 = Thread(target=self.watchdog, args=(session0, schema))
        t1.start()
        try:
            engine1, session1 = self.create_transaction(url, "transaction1")
            session1.execute("SELECT 1")

            session1.execute("SELECT * FROM %s.deadlock_test2" % schema)
            session1.execute("INSERT INTO %s.deadlock_test1 VALUES 2" % schema)

            engine3, session3 = self.create_transaction(url, "transaction3")
            session3.execute("SELECT 1")
            session3.execute("DELETE FROM %s.deadlock_test2 WHERE false" % schema)
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
            session0.execute("DROP SCHEMA %s cascade" % schema)
        except:
            pass
        session0.execute("CREATE SCHEMA %s" % schema)
        session0.execute("CREATE OR REPLACE TABLE %s.deadlock_test_table (id int)" % schema)
        session0.execute(
            "CREATE OR REPLACE VIEW %s.deadlock_test_view_1 AS SELECT * FROM %s.deadlock_test_table" % (schema, schema))
        session0.execute("commit")
        self.watchdog_run = True
        t1 = Thread(target=self.watchdog, args=(session0, schema))
        t1.start()
        try:
            engine1, session1 = self.create_transaction(url, "transaction1")
            session1.execute("SELECT 1")

            session1.execute("SELECT * FROM %s.deadlock_test_view_1" % schema)
            session1.execute(
                "CREATE OR REPLACE VIEW %s.deadlock_test_view_2 AS SELECT * FROM %s.deadlock_test_table" % (
                    schema, schema))

            engine3, session3 = self.create_transaction(url, "transaction3")
            session3.execute("SELECT 1")
            session3.execute("DROP VIEW %s.deadlock_test_view_1" % schema)
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
