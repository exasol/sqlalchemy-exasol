# -*- coding: UTF-8 -*-
import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, Date, DateTime, ForeignKeyConstraint, create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import or_, select, literal_column
from sqlalchemy import testing, inspect
from sqlalchemy.schema import DropConstraint, AddConstraint
from sqlalchemy.testing import fixtures, config

from sqlalchemy_exasol.base import EXAExecutionContext, EXADialect
from sqlalchemy_exasol.constraints import DistributeByConstraint
from sqlalchemy_exasol.merge import merge
from sqlalchemy_exasol.util import raw_sql

from threading import Thread
import time
import pytest

class MetadataTest(fixtures.TablesTest):
    __backend__ = True

    def create_transaction(self, url, con_name):
        engine=create_engine(config.db.url, echo=True, logging_name="engine"+con_name)
        session=engine.connect().execution_options(autocommit=False)
        return engine, session

    def test_deadlock_for_get_table_names(self):
        def without_fallback(session2,schema):
            dialect=EXADialect()
            dialect.get_table_names(session2, schema=schema, use_sql_fallback=False)

        def with_fallback(session2,schema):
            dialect=EXADialect()
            dialect.get_table_names(session2, schema=schema, use_sql_fallback=True)

        self.run_deadlock(without_fallback)
        with pytest.raises(Exception):
            self.run_deadlock(with_fallback)
    
    def test_deadlock_for_get_view_names(self):
        def without_fallback(session2,schema):
            dialect=EXADialect()
            dialect.get_view_names(session2, schema=schema, use_sql_fallback=False)

        def with_fallback(session2,schema):
            dialect=EXADialect()
            dialect.get_view_names(session2, schema=schema, use_sql_fallback=True)

        self.run_deadlock(without_fallback)
        with pytest.raises(Exception):
            self.run_deadlock(with_fallback)

    def watchdog(self, session0, schema):
        while self.watchdog_run:
            rs=session0.execute("SELECT * FROM SYS.EXA_ALL_SESSIONS")
            rs=[row for row in rs]
            print()
            print("===========================================")
            print("Watchdog")
            print("===========================================")
            for row in rs:
                print(row)
                if row[7] is not None and "Waiting for" in row[7]:
                    print("Killing session: %s"%row[0])
                    session0.execute("kill session %s"%row[0])
            print("===========================================")
            print()
            time.sleep(10)

    def run_deadlock(self,function):
        c1=config.db.connect()
        url=config.db.url

        schema="deadlock_test_schema"
        engine0, session0 = self.create_transaction(url, "transaction0")
        try:
            session0.execute("DROP SCHEMA %s cascade"%schema)
        except:
            pass
        session0.execute("CREATE SCHEMA %s"%schema)
        session0.execute("CREATE OR REPLACE TABLE %s.deadlock_test1 (id int)"%schema)
        session0.execute("CREATE OR REPLACE TABLE %s.deadlock_test2 (id int)"%schema)
        session0.execute("INSERT INTO %s.deadlock_test2 VALUES 2"%schema)
        session0.execute("commit")
        self.watchdog_run=True
        t1=Thread(target=self.watchdog,args=(session0,schema))
        t1.start()
        try:
            engine1, session1 = self.create_transaction(url, "transaction1")
            session1.execute("SELECT 1")

            session1.execute("SELECT * FROM %s.deadlock_test2"%schema)
            session1.execute("INSERT INTO %s.deadlock_test1 VALUES 1"%schema)
            
            engine3, session3 = self.create_transaction(url, "transaction3")
            session3.execute("SELECT 1")
            session3.execute("DELETE FROM %s.deadlock_test2 WHERE false"%schema)
            session3.execute("commit")

            
            engine2, session2 = self.create_transaction(url, "transaction2")
            session2.execute("SELECT 1")
            function(session2,schema)
            
            session2.execute("commit")
            session1.execute("commit")
        except Exception as e:
            self.watchdog_run=False
            t1.join()
            raise e
        self.watchdog_run=False
        t1.join()
