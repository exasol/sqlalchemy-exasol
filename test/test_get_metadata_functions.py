# -*- coding: UTF-8 -*-
import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, Date, DateTime, ForeignKeyConstraint
from sqlalchemy import or_, select, literal_column
from sqlalchemy import testing, inspect
from sqlalchemy.schema import DropConstraint, AddConstraint
from sqlalchemy.testing import fixtures, config

from sqlalchemy_exasol.base import EXAExecutionContext, EXADialect
from sqlalchemy_exasol.constraints import DistributeByConstraint
from sqlalchemy_exasol.merge import merge
from sqlalchemy_exasol.util import raw_sql



class MetadataTest(fixtures.TablesTest):
    __backend__ = True

    
    @classmethod
    def define_tables(cls, metadata):
        t=Table('t', metadata,
            Column('pid1', Integer,  primary_key=True),
            Column('pid2', Integer,  primary_key=True),
            Column('name', String(20)),
            Column('age', Integer)
        )
        Table('s', metadata,
            Column('id', Integer),
            Column('fid1', Integer),
            Column('fid2', Integer),
            Column('age', Integer),
            ForeignKeyConstraint(
            ['fid1','fid2'], ['t.pid1','t.pid2'],
            name='fk_test')
        )


    def test_compare_get_table_names_for_sql_and_odbc(self):
        c=config.db.connect()
        dialect=EXADialect()
        table_names_fallback = dialect.get_table_names(connection=c, schema=None, use_sql_fallback=True)
        table_names_odbc = dialect.get_table_names(connection=c, schema=None)
        assert table_names_fallback == table_names_odbc
    
    def test_compare_get_view_names_for_sql_and_odbc(self):
        c=config.db.connect()
        c.execute("CREATE OR REPLACE VIEW v AS select * from t")
        dialect=EXADialect()
        view_names_fallback = dialect.get_view_names(connection=c, schema=None, use_sql_fallback=True)
        view_names_odbc = dialect.get_view_names(connection=c, schema=None)
        assert view_names_fallback == view_names_odbc

    def test_compare_get_view_definition_for_sql_and_odbc(self):
        c=config.db.connect()
        c.execute("CREATE OR REPLACE VIEW v AS select * from t")
        view_name="v"
        dialect=EXADialect()
        view_definition_fallback = dialect.get_view_definition(
                connection=c, view_name=view_name, schema=None, use_sql_fallback=True)
        view_definition_odbc = dialect.get_view_definition(
                connection=c, view_name=view_name, schema=None)
        assert view_definition_fallback == view_definition_odbc

    def test_compare_get_columns_for_sql_and_odbc(self):
        c=config.db.connect()
        dialect=EXADialect()
        columns_fallback = dialect.get_columns(connection=c, table_name="t", schema=None, use_sql_fallback=True)
        columns_odbc = dialect.get_columns(connection=c, table_name="t", schema=None)
        assert str(columns_fallback) == str(columns_odbc) #object equallity doesn't work for some reason

    def test_compare_get_pk_constraint_for_sql_and_odbc(self):
        c=config.db.connect()
        dialect=EXADialect()
        pk_constraint_fallback = dialect.get_pk_constraint(connection=c, table_name="t", schema=None, use_sql_fallback=True)
        pk_constraint_odbc = dialect.get_pk_constraint(connection=c, table_name="t", schema=None)
        assert str(pk_constraint_fallback) == str(pk_constraint_odbc)

    def test_compare_get_foreign_keys_for_sql_and_odbc(self):
        c=config.db.connect()
        dialect=EXADialect()
        foreign_keys_fallback = dialect.get_foreign_keys(connection=c, table_name="t", schema=None, use_sql_fallback=True)
        foreign_keys_odbc = dialect.get_foreign_keys(connection=c, table_name="t", schema=None)
        assert str(foreign_keys_fallback) == str(foreign_keys_odbc)

    # def test_alter_table_distribute_by(self):
    #     for table in config.db.table_names():
    #         print("TABLE",table)
    #     insp = inspect(config.db)
    #     for schema in insp.get_schema_names():
    #         print("SCHEMA_engine",schema)
    #     c=config.db.connect()
    #     insp = inspect(c)
    #     for schema in insp.get_schema_names():
    #         print("SCHEMA_conn",schema)
    #     for view in insp.get_view_names():
    #         print("VIEW_conn",view)
    #         print(insp.get_view_definition(view))
    #     print("Columns for table",insp.get_table_names()[0])
    #     for column in insp.get_columns(table_name=insp.get_table_names()[0]):
    #         print("COLUMN",column)
    #     print("pk",insp.get_pk_constraint("pk_test"))
     
    #     config.db.execute("commit")
    #     print("fk",insp.get_foreign_keys("fk_test"))
