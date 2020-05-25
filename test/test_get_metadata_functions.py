# -*- coding: UTF-8 -*-

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.sql.sqltypes import INTEGER, VARCHAR
from sqlalchemy.testing import fixtures, config

from sqlalchemy_exasol.base import EXADialect

TEST_GET_METADATA_FUNCTIONS_SCHEMA = "test_get_metadata_functions_schema"
ENGINE_NONE_DATABASE = "ENGINE_NONE_DATABASE"
ENGINE_SCHEMA_DATABASE = "ENGINE_SCHEMA_DATABASE"
ENGINE_SCHEMA_2_DATABASE = "ENGINE_SCHEMA_2_DATABASE"


class MetadataTest(fixtures.TablesTest):
    __backend__ = True

    @classmethod
    def define_tables(cls, metadata):
        cls.schema = TEST_GET_METADATA_FUNCTIONS_SCHEMA
        cls.schema_2 = "test_get_metadata_functions_schema_2"
        with config.db.begin() as c:
            try:
                c.execute("DROP SCHEMA %s CASCADE" % cls.schema)
            except Exception as e:
                print(e)
                pass
            c.execute("CREATE SCHEMA %s" % cls.schema)
            c.execute(
                "CREATE TABLE %s.t (pid1 int, pid2 int, name VARCHAR(20), age int, PRIMARY KEY (pid1,pid2))" % cls.schema)
            c.execute(
                "CREATE TABLE {schema}.s (id1 int primary key, fid1 int, fid2 int, age int, CONSTRAINT fk_test FOREIGN KEY (fid1,fid2) REFERENCES {schema}.t(pid1,pid2))".format(
                    schema=cls.schema))
            cls.view_defintion = "CREATE VIEW {schema}.v AS select * from {schema}.t".format(schema=cls.schema)
            c.execute(cls.view_defintion)

            try:
                c.execute("DROP SCHEMA %s CASCADE" % cls.schema_2)
            except Exception as e:
                print(e)
                pass
            c.execute("CREATE SCHEMA %s" % cls.schema_2)
            c.execute(
                "CREATE TABLE %s.t_2 (pid1 int, pid2 int, name VARCHAR(20), age int, PRIMARY KEY (pid1,pid2))" % cls.schema_2)
            c.execute("CREATE VIEW {schema}.v_2 AS select * from {schema}.t_2".format(schema=cls.schema_2))
            c.execute("COMMIT")

            cls.engine_none_database = cls.create_engine_with_database_name(c, None)
            cls.engine_schema_database = cls.create_engine_with_database_name(c, cls.schema)
            cls.engine_schema_2_database = cls.create_engine_with_database_name(c, cls.schema_2)
            cls.engine_map = {
                ENGINE_NONE_DATABASE: cls.engine_none_database,
                ENGINE_SCHEMA_DATABASE: cls.engine_schema_database,
                ENGINE_SCHEMA_2_DATABASE: cls.engine_schema_2_database
            }

    @classmethod
    def generate_url_with_database_name(cls, connection, new_database_name):
        database_url = config.db_url
        new_args = database_url.translate_connect_args()
        new_args["database"] = new_database_name
        new_database_url = URL(drivername=database_url.drivername, query=database_url.query, **new_args)
        return new_database_url

    @classmethod
    def create_engine_with_database_name(cls, connection, new_database_name):
        url = cls.generate_url_with_database_name(connection, new_database_name)
        engine = create_engine(url)
        return engine

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_get_schema_names(self, engine_name, use_sql_fallback):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            schema_names = dialect.get_schema_names(connection=c, use_sql_fallback=use_sql_fallback)
            assert self.schema in schema_names and self.schema_2 in schema_names

    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_compare_get_schema_names_for_sql_and_odbc(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            schema_names_fallback = dialect.get_schema_names(connection=c, use_sql_fallback=True)
            schema_names_odbc = dialect.get_schema_names(connection=c)
            assert sorted(schema_names_fallback) == sorted(schema_names_odbc)

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_get_table_names(self, use_sql_fallback, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            table_names = dialect.get_table_names(connection=c, schema=self.schema, use_sql_fallback=use_sql_fallback)
            assert "t" in table_names and "s" in table_names

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_compare_get_table_names_for_sql_and_odbc(self, schema, engine_name):
        with self.engine_map[engine_name].begin() as c:
            if schema is None:
                c.execute("OPEN SCHEMA %s" % self.schema)
            dialect = EXADialect()
            table_names_fallback = dialect.get_table_names(connection=c, schema=schema, use_sql_fallback=True)
            table_names_odbc = dialect.get_table_names(connection=c, schema=schema)
            assert table_names_fallback == table_names_odbc

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_has_table_table_exists(self, use_sql_fallback, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            has_table = dialect.has_table(connection=c, schema=self.schema, table_name="t",
                                          use_sql_fallback=use_sql_fallback)
            assert has_table, "Table %s.T was not found, but should exist" % self.schema

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_has_table_table_exists_not(self, use_sql_fallback, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            has_table = dialect.has_table(connection=c, schema=self.schema, table_name="not_exist",
                                          use_sql_fallback=use_sql_fallback)
            assert not has_table, "Table %s.not_exist was found, but should not exist" % self.schema

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_compare_has_table_for_sql_and_odbc(self, schema, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            has_table_fallback = dialect.has_table(connection=c, schema=schema, use_sql_fallback=True, table_name="t")
            has_table_odbc = dialect.has_table(connection=c, schema=schema, table_name="t")
            assert has_table_fallback == has_table_odbc, "Expected table %s.t with odbc and fallback" % schema

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_get_view_names(self, use_sql_fallback,engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            view_names = dialect.get_view_names(connection=c, schema=self.schema, use_sql_fallback=use_sql_fallback)
            assert "v" in view_names

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_get_view_names_for_sys(self, use_sql_fallback, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            view_names = dialect.get_view_names(connection=c, schema="sys", use_sql_fallback=use_sql_fallback)
            assert len(view_names) == 0

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_get_view_definition(self, use_sql_fallback,engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            view_definition = dialect.get_view_definition(connection=c, schema=self.schema, view_name="v",
                                                          use_sql_fallback=use_sql_fallback)
            assert self.view_defintion == view_definition

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_get_view_definition_view_name_none(self, use_sql_fallback,engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            view_definition = dialect.get_view_definition(connection=c, schema=self.schema, view_name=None,
                                                          use_sql_fallback=use_sql_fallback)
            assert view_definition is None

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_compare_get_view_names_for_sql_and_odbc(self, schema,engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            c.execute("OPEN SCHEMA %s" % self.schema)
            view_names_fallback = dialect.get_view_names(connection=c, schema=schema, use_sql_fallback=True)
            view_names_odbc = dialect.get_view_names(connection=c, schema=schema)
            assert view_names_fallback == view_names_odbc

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_compare_get_view_definition_for_sql_and_odbc(self, schema,engine_name):
        with self.engine_map[engine_name].begin() as c:
            if schema is None:
                c.execute("OPEN SCHEMA %s" % self.schema)
            view_name = "v"
            dialect = EXADialect()
            view_definition_fallback = dialect.get_view_definition(
                connection=c, view_name=view_name, schema=schema, use_sql_fallback=True)
            view_definition_odbc = dialect.get_view_definition(
                connection=c, view_name=view_name, schema=schema)
            assert view_definition_fallback == view_definition_odbc

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    @pytest.mark.parametrize("table", ["t", "s", "unknown"])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_compare_get_columns_for_sql_and_odbc(self, schema, table, engine_name):
        with self.engine_map[engine_name].begin() as c:
            if schema is None:
                c.execute("OPEN SCHEMA %s" % self.schema)
            dialect = EXADialect()
            columns_fallback = dialect.get_columns(connection=c, table_name=table, schema=schema, use_sql_fallback=True)
            columns_odbc = dialect.get_columns(connection=c, table_name=table, schema=schema)
            assert str(columns_fallback) == str(columns_odbc)  # object equality doesn't work for sqltypes

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_compare_get_columns_none_table_for_sql_and_odbc(self, schema, engine_name):
        with self.engine_map[engine_name].begin() as c:
            if schema is None:
                c.execute("OPEN SCHEMA %s" % self.schema)
            dialect = EXADialect()
            table = None
            columns_fallback = dialect.get_columns(connection=c, table_name=table, schema=schema,
                                                   use_sql_fallback=True)
            columns_odbc = dialect.get_columns(connection=c, table_name=table, schema=schema)
            assert str(columns_fallback) == str(columns_odbc)  # object equality doesn't work for sqltypes

    def make_columns_comparable(self, column_list):  # object equality doesn't work for sqltypes
        return sorted([{k: str(v) for k, v in column.items()} for column in column_list], key=lambda k: k["name"])

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_get_columns(self, use_sql_fallback, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            columns = dialect.get_columns(connection=c, schema=self.schema, table_name="t",
                                          use_sql_fallback=use_sql_fallback)
            expected = [{'default': None,
                         'is_distribution_key': False,
                         'name': 'pid1',
                         'nullable': False,
                         'type': INTEGER()},
                        {'default': None,
                         'is_distribution_key': False,
                         'name': 'pid2',
                         'nullable': False,
                         'type': INTEGER()},
                        {'default': None,
                         'is_distribution_key': False,
                         'name': 'name',
                         'nullable': True,
                         'type': VARCHAR(length=20)},
                        {'default': None,
                         'is_distribution_key': False,
                         'name': 'age',
                         'nullable': True,
                         'type': INTEGER()},
                        ]

            assert self.make_columns_comparable(expected) == self.make_columns_comparable(columns)

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_get_columns_table_name_none(self, use_sql_fallback, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            columns = dialect.get_columns(connection=c, schema=self.schema, table_name=None,
                                          use_sql_fallback=use_sql_fallback)
            expected = [
                # Table S
                {'default': None,
                 'is_distribution_key': False,
                 'name': 'id1',
                 'nullable': False,
                 'type': INTEGER()},
                {'default': None,
                 'is_distribution_key': False,
                 'name': 'fid1',
                 'nullable': True,
                 'type': INTEGER()},
                {'default': None,
                 'is_distribution_key': False,
                 'name': 'fid2',
                 'nullable': True,
                 'type': INTEGER()},
                {'default': None,
                 'is_distribution_key': False,
                 'name': 'age',
                 'nullable': True,
                 'type': INTEGER()},
                # Table T
                {'default': None,
                 'is_distribution_key': False,
                 'name': 'pid1',
                 'nullable': False,
                 'type': INTEGER()},
                {'default': None,
                 'is_distribution_key': False,
                 'name': 'pid2',
                 'nullable': False,
                 'type': INTEGER()},
                {'default': None,
                 'is_distribution_key': False,
                 'name': 'age',
                 'nullable': True,
                 'type': INTEGER()},
                {'default': None,
                 'is_distribution_key': False,
                 'name': 'name',
                 'nullable': True,
                 'type': VARCHAR(length=20)},
                # view v adds additional columns
                {'default': None,
                 'is_distribution_key': None,
                 'name': 'pid1',
                 'nullable': None,
                 'type': INTEGER()},
                {'default': None,
                 'is_distribution_key': None,
                 'name': 'pid2',
                 'nullable': None,
                 'type': INTEGER()},
                {'default': None,
                 'is_distribution_key': None,
                 'name': 'name',
                 'nullable': None,
                 'type': VARCHAR(length=20)},
                {'default': None,
                 'is_distribution_key': None,
                 'name': 'age',
                 'nullable': None,
                 'type': INTEGER()},
            ]
            assert self.make_columns_comparable(expected) == self.make_columns_comparable(columns)

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    @pytest.mark.parametrize("table", ["t", "s"])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_compare_get_pk_constraint_for_sql_and_odbc(self, schema, table, engine_name):
        with self.engine_map[engine_name].begin() as c:
            if schema is None:
                c.execute("OPEN SCHEMA %s" % self.schema)
            dialect = EXADialect()
            pk_constraint_fallback = dialect.get_pk_constraint(connection=c, table_name=table, schema=schema,
                                                               use_sql_fallback=True)
            pk_constraint_odbc = dialect.get_pk_constraint(connection=c, table_name=table, schema=schema)
            assert str(pk_constraint_fallback) == str(pk_constraint_odbc)

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_get_pk_constraint(self, use_sql_fallback, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            pk_constraint = dialect.get_pk_constraint(connection=c, schema=self.schema, table_name="t",
                                                      use_sql_fallback=use_sql_fallback)
            assert pk_constraint["constrained_columns"] == ['pid1', 'pid2'] and \
                   pk_constraint["name"].startswith("sys_")

    @pytest.mark.parametrize("table", ["t", "s", None])
    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_compare_get_foreign_keys_for_sql_and_odbc(self, schema, table, engine_name):
        with self.engine_map[engine_name].begin() as c:
            if schema is None:
                c.execute("OPEN SCHEMA %s" % self.schema_2)
            dialect = EXADialect()
            foreign_keys_fallback = dialect.get_foreign_keys(connection=c, table_name=table, schema=schema,
                                                             use_sql_fallback=True)
            foreign_keys_odbc = dialect.get_foreign_keys(connection=c, table_name=table, schema=schema)
            assert str(foreign_keys_fallback) == str(foreign_keys_odbc)

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_get_foreign_keys(self, use_sql_fallback, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            foreign_keys = dialect.get_foreign_keys(connection=c, schema=self.schema, table_name="s",
                                                    use_sql_fallback=use_sql_fallback)
            expected = [{'name': 'fk_test',
                         'constrained_columns': ['fid1', 'fid2'],
                         'referred_schema': 'test_get_metadata_functions_schema',
                         'referred_table': 't',
                         'referred_columns': ['pid1', 'pid2']}]

            assert foreign_keys == expected

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    @pytest.mark.parametrize("engine_name", [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE])
    def test_get_foreign_keys_table_name_none(self, use_sql_fallback, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = EXADialect()
            foreign_keys = dialect.get_foreign_keys(connection=c, schema=self.schema, table_name=None,
                                                    use_sql_fallback=use_sql_fallback)
            expected = [{'name': 'fk_test',
                         'constrained_columns': ['fid1', 'fid2'],
                         'referred_schema': 'test_get_metadata_functions_schema',
                         'referred_table': 't',
                         'referred_columns': ['pid1', 'pid2']}]

            assert foreign_keys == expected
