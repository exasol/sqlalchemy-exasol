# -*- coding: UTF-8 -*-
import pytest
from sqlalchemy.sql.sqltypes import INTEGER, VARCHAR
from sqlalchemy.testing import fixtures, config

from sqlalchemy_exasol.base import EXADialect

TEST_GET_METADATA_FUNCTIONS_SCHEMA = "test_get_metadata_functions_schema"


class MetadataTest(fixtures.TablesTest):
    __backend__ = True

    @classmethod
    def define_tables(cls, metadata):
        cls.schema = TEST_GET_METADATA_FUNCTIONS_SCHEMA
        cls.schema_2 = "test_get_metadata_functions_schema_2"
        c = config.db.connect()
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

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    def test_get_schema_names(self, use_sql_fallback):
        c = config.db.connect()
        dialect = EXADialect()
        schema_names = dialect.get_schema_names(connection=c, use_sql_fallback=use_sql_fallback)
        assert self.schema in schema_names and self.schema_2 in schema_names

    def test_compare_get_schema_names_for_sql_and_odbc(self):
        c = config.db.connect()
        dialect = EXADialect()
        schema_names_fallback = dialect.get_schema_names(connection=c, use_sql_fallback=True)
        schema_names_odbc = dialect.get_schema_names(connection=c)
        assert sorted(schema_names_fallback) == sorted(schema_names_odbc)

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    def test_get_table_names(self, use_sql_fallback):
        c = config.db.connect()
        dialect = EXADialect()
        table_names = dialect.get_table_names(connection=c, schema=self.schema, use_sql_fallback=use_sql_fallback)
        assert "t" in table_names and "s" in table_names

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    def test_compare_get_table_names_for_sql_and_odbc(self, schema):
        c = config.db.connect()
        dialect = EXADialect()
        table_names_fallback = dialect.get_table_names(connection=c, schema=schema, use_sql_fallback=True)
        table_names_odbc = dialect.get_table_names(connection=c, schema=schema)
        assert table_names_fallback == table_names_odbc

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    def test_get_view_names(self, use_sql_fallback):
        c = config.db.connect()
        dialect = EXADialect()
        view_names = dialect.get_view_names(connection=c, schema=self.schema, use_sql_fallback=use_sql_fallback)
        assert "v" in view_names

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    def test_get_view_definition(self, use_sql_fallback):
        c = config.db.connect()
        dialect = EXADialect()
        view_definition = dialect.get_view_definition(connection=c, schema=self.schema, view_name="v",
                                                      use_sql_fallback=use_sql_fallback)
        assert self.view_defintion == view_definition

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    def test_get_view_definition_view_name_none(self, use_sql_fallback):
        c = config.db.connect()
        dialect = EXADialect()
        view_definition = dialect.get_view_definition(connection=c, schema=self.schema, view_name=None,
                                                      use_sql_fallback=use_sql_fallback)
        assert view_definition is None

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    def test_compare_get_view_names_for_sql_and_odbc(self, schema):
        c = config.db.connect()
        dialect = EXADialect()
        view_names_fallback = dialect.get_view_names(connection=c, schema=schema, use_sql_fallback=True)
        view_names_odbc = dialect.get_view_names(connection=c, schema=schema)
        assert view_names_fallback == view_names_odbc

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    def test_compare_get_view_definition_for_sql_and_odbc(self, schema):
        c = config.db.connect()
        view_name = "v"
        dialect = EXADialect()
        view_definition_fallback = dialect.get_view_definition(
            connection=c, view_name=view_name, schema=schema, use_sql_fallback=True)
        view_definition_odbc = dialect.get_view_definition(
            connection=c, view_name=view_name, schema=schema)
        assert view_definition_fallback == view_definition_odbc

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    @pytest.mark.parametrize("table", ["t", "s", "unknown"])
    def test_compare_get_columns_for_sql_and_odbc(self, schema, table):
        c = config.db.connect()
        dialect = EXADialect()
        columns_fallback = dialect.get_columns(connection=c, table_name=table, schema=schema, use_sql_fallback=True)
        columns_odbc = dialect.get_columns(connection=c, table_name=table, schema=schema)
        assert str(columns_fallback) == str(columns_odbc)  # object equality doesn't work for sqltypes

    def test_compare_get_columns_none_table_for_sql_and_odbc(self, ):
        c = config.db.connect()
        dialect = EXADialect()
        table = None
        columns_fallback = dialect.get_columns(connection=c, table_name=table, schema=self.schema,
                                               use_sql_fallback=True)
        columns_odbc = dialect.get_columns(connection=c, table_name=table, schema=self.schema)
        assert str(columns_fallback) == str(columns_odbc)  # object equality doesn't work for sqltypes

    def make_columns_comparable(self, column_list):  # object equality doesn't work for sqltypes
        return sorted([{k: str(v) for k, v in column.items()} for column in column_list], key=lambda k: k["name"])

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    def test_get_columns(self, use_sql_fallback):
        c = config.db.connect()
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
    def test_get_columns_table_name_none(self, use_sql_fallback):
        c = config.db.connect()
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
    def test_compare_get_pk_constraint_for_sql_and_odbc(self, schema, table):
        c = config.db.connect()
        dialect = EXADialect()
        pk_constraint_fallback = dialect.get_pk_constraint(connection=c, table_name=table, schema=schema,
                                                           use_sql_fallback=True)
        pk_constraint_odbc = dialect.get_pk_constraint(connection=c, table_name=table, schema=schema)
        assert str(pk_constraint_fallback) == str(pk_constraint_odbc)

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    def test_get_pk_constraint(self, use_sql_fallback):
        c = config.db.connect()
        dialect = EXADialect()
        pk_constraint = dialect.get_pk_constraint(connection=c, schema=self.schema, table_name="t",
                                                  use_sql_fallback=use_sql_fallback)
        assert pk_constraint["constrained_columns"] == ['pid1', 'pid2'] and \
               pk_constraint["name"].startswith("sys_")

    @pytest.mark.parametrize("schema", [TEST_GET_METADATA_FUNCTIONS_SCHEMA, None])
    @pytest.mark.parametrize("table", ["t", "s", None])
    def test_compare_get_foreign_keys_for_sql_and_odbc(self, schema, table):
        c = config.db.connect()
        dialect = EXADialect()
        foreign_keys_fallback = dialect.get_foreign_keys(connection=c, table_name=table, schema=schema,
                                                         use_sql_fallback=True)
        foreign_keys_odbc = dialect.get_foreign_keys(connection=c, table_name=table, schema=schema)
        assert str(foreign_keys_fallback) == str(foreign_keys_odbc)

    @pytest.mark.parametrize("use_sql_fallback", [True, False])
    def test_get_foreign_keys(self, use_sql_fallback):
        c = config.db.connect()
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
    def test_get_foreign_keys_table_name_nont(self, use_sql_fallback):
        c = config.db.connect()
        dialect = EXADialect()
        foreign_keys = dialect.get_foreign_keys(connection=c, schema=self.schema, table_name=None,
                                                use_sql_fallback=use_sql_fallback)
        expected = [{'name': 'fk_test',
                     'constrained_columns': ['fid1', 'fid2'],
                     'referred_schema': 'test_get_metadata_functions_schema',
                     'referred_table': 't',
                     'referred_columns': ['pid1', 'pid2']}]

        assert foreign_keys == expected
