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
        cls.schema="test_get_metadata_functions_schema"
        cls.schema_2="test_get_metadata_functions_schema"
        c=config.db.connect()
        try:
            c.execute("DROP SCHEMA %s CASCADE"%cls.schema)
        except:
            pass
        c.execute("CREATE SCHEMA %s"%cls.schema)
        c.execute("CREATE TABLE %s.t (pid1 int, pid2 int, name VARCHAR(20), age int, PRIMARY KEY (pid1,pid2))"%cls.schema)
        c.execute("CREATE TABLE {schema}.s (id1 int primary key, fid1 int, fid2 int, age int, CONSTRAINT fk_test FOREIGN KEY (fid1,fid2) REFERENCES {schema}.t(pid1,pid2))".format(schema=cls.schema))
        c.execute("CREATE VIEW {schema}.v AS select * from {schema}.t".format(schema=cls.schema))
        
        try:
            c.execute("DROP SCHEMA %s CASCADE"%cls.schema_2)
        except:
            pass
        c.execute("CREATE SCHEMA %s"%cls.schema_2)
        c.execute("CREATE TABLE %s.t_2 (pid1 int, pid2 int, name VARCHAR(20), age int, PRIMARY KEY (pid1,pid2))"%cls.schema_2)
        c.execute("CREATE VIEW {schema}.v_2 AS select * from {schema}.t_2".format(schema=cls.schema_2))

 
    def test_compare_get_table_names_for_sql_and_odbc_schema_given(self):
        self.run_compare_get_table_names_for_sql_and_odbc(self.schema)

    def test_compare_get_table_names_for_sql_and_odbc_schema_not_given(self):
        self.run_compare_get_table_names_for_sql_and_odbc(None)

    def run_compare_get_table_names_for_sql_and_odbc(self,schema):
        c=config.db.connect()
        dialect=EXADialect()
        table_names_fallback = dialect.get_table_names(connection=c, schema=schema, use_sql_fallback=True)
        table_names_odbc = dialect.get_table_names(connection=c, schema=schema)
        assert table_names_fallback == table_names_odbc

    def test_compare_get_view_names_for_sql_and_odbc_schema_given(self):
        self.run_compare_get_view_names_for_sql_and_odbc(self.schema)

    def test_compare_get_view_names_for_sql_and_odbc_schema_not_given(self):
        self.run_compare_get_view_names_for_sql_and_odbc(None)
    
    def run_compare_get_view_names_for_sql_and_odbc(self, schema):
        c=config.db.connect()
        dialect=EXADialect()
        view_names_fallback = dialect.get_view_names(connection=c, schema=schema, use_sql_fallback=True)
        view_names_odbc = dialect.get_view_names(connection=c, schema=schema)
        assert view_names_fallback == view_names_odbc


    def test_compare_get_view_definition_for_sql_and_odbc_schema_given(self):
        self.run_compare_get_view_definition_for_sql_and_odbc(self.schema)

    def test_compare_get_view_defintion_for_sql_and_odbc_schema_not_given(self):
        self.run_compare_get_view_definition_for_sql_and_odbc(None)

    def run_compare_get_view_definition_for_sql_and_odbc(self,schema):
        c=config.db.connect()
        view_name="v"
        dialect=EXADialect()
        view_definition_fallback = dialect.get_view_definition(
                connection=c, view_name=view_name, schema=schema, use_sql_fallback=True)
        view_definition_odbc = dialect.get_view_definition(
                connection=c, view_name=view_name, schema=schema)
        assert view_definition_fallback == view_definition_odbc

    def test_compare_get_columns_for_sql_and_odbc_schema_given(self):
        self.run_compare_get_columns_for_sql_and_odbc(self.schema)

    def test_compare_get_columns_for_sql_and_odbc_schema_not_given(self):
        self.run_compare_get_columns_for_sql_and_odbc(None)

    def run_compare_get_columns_for_sql_and_odbc(self,schema):
        c=config.db.connect()
        dialect=EXADialect()
        columns_fallback = dialect.get_columns(connection=c, table_name="t", schema=schema, use_sql_fallback=True)
        columns_odbc = dialect.get_columns(connection=c, table_name="t", schema=schema)
        assert str(columns_fallback) == str(columns_odbc) #object equallity doesn't work for some reason

    def test_compare_get_pk_constraint_for_sql_and_odbc_schema_given(self):
        self.run_compare_get_pk_constraint_for_sql_and_odbc(self.schema)

    def test_compare_get_pk_constraint_for_sql_and_odbc_schema_not_given(self):
        self.run_compare_get_pk_constraint_for_sql_and_odbc(None)

    def run_compare_get_pk_constraint_for_sql_and_odbc(self,schema):
        c=config.db.connect()
        dialect=EXADialect()
        pk_constraint_fallback = dialect.get_pk_constraint(connection=c, table_name="t", schema=schema, use_sql_fallback=True)
        pk_constraint_odbc = dialect.get_pk_constraint(connection=c, table_name="t", schema=schema)
        assert str(pk_constraint_fallback) == str(pk_constraint_odbc)

    def test_compare_get_foreign_keys_for_sql_and_odbc_schema_given(self):
        self.run_compare_get_foreign_keys_for_sql_and_odbc(self.schema)

    def test_compare_get_foreign_keys_for_sql_and_odbc_schema_not_given(self):
        self.run_compare_get_foreign_keys_for_sql_and_odbc(None)

    def run_compare_get_foreign_keys_for_sql_and_odbc(self,schema):
        c=config.db.connect()
        dialect=EXADialect()
        foreign_keys_fallback = dialect.get_foreign_keys(connection=c, table_name="t", schema=schema, use_sql_fallback=True)
        foreign_keys_odbc = dialect.get_foreign_keys(connection=c, table_name="t", schema=schema)
        assert str(foreign_keys_fallback) == str(foreign_keys_odbc)
