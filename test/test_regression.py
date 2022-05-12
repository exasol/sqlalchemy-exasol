"""This module contains various regression test for issues which have been fixed in the past"""
import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, inspect
from sqlalchemy.pool import (
    AssertionPool,
    NullPool,
    QueuePool,
    SingletonThreadPool,
    StaticPool,
)
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy.testing import fixtures
from sqlalchemy.testing.fixtures import config


class TranslateMap(fixtures.TestBase):
    @classmethod
    def setup_class(cls):
        cls.table_name = "my_table"
        cls.tenant_schema_name = "tenant_schema"
        engine = config.db
        with config.db.connect() as conn:
            conn.execute(CreateSchema(cls.tenant_schema_name))
            metadata = MetaData()
            Table(
                cls.table_name,
                metadata,
                Column("id", Integer, primary_key=True),
                Column("name", String(1000), nullable=False),
                schema=cls.tenant_schema_name,
            )
            metadata.create_all(engine)

    @classmethod
    def teardown_class(cls):
        with config.db.connect() as conn:
            conn.execute(DropSchema(cls.tenant_schema_name, cascade=True))

    def test_use_schema_translate_map_in_get_last_row_id(self):
        """See also: https://github.com/exasol/sqlalchemy-exasol/issues/104"""
        schema_name = "some_none_existent_schema"
        options = {"schema_translate_map": {schema_name: self.tenant_schema_name}}
        metadata = MetaData()
        my_table = Table(
            self.table_name,
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(1000), nullable=False),
            schema=schema_name,
        )
        engine = create_engine(config.db.url, execution_options=options)
        with engine.connect() as conn:
            conn.execute(my_table.insert().values(name="John Doe"))


class Introspection(fixtures.TestBase):
    """Regression(s) for issue: https://github.com/exasol/sqlalchemy-exasol/issues/136"""

    POOL_TYPES = [
        QueuePool,
        NullPool,
        AssertionPool,
        StaticPool,
        SingletonThreadPool,
    ]

    @classmethod
    def setup_class(cls):
        def _create_tables(schema, tables):
            engine = config.db
            with engine.connect():
                metadata = MetaData()
                for name in tables:
                    Table(
                        name,
                        metadata,
                        Column("id", Integer, primary_key=True),
                        Column("random_field", String(1000)),
                        schema=schema,
                    )
                metadata.create_all(engine)

        def _create_views(schema, views):
            engine = config.db
            with engine.connect() as conn:
                for name in views:
                    conn.execute(
                        f"CREATE OR REPLACE VIEW {schema}.{name} AS SELECT 1 as COLUMN_1;"
                    )

        cls.schema = "test"
        cls.tables = ["a_table", "b_table", "c_table", "d_table"]
        cls.views = ["a_view", "b_view"]

        _create_tables(cls.schema, cls.tables)
        _create_views(cls.schema, cls.views)

    @classmethod
    def teardown_class(cls):
        engine = config.db

        def _drop_tables(schema):
            metadata = MetaData(engine, schema=schema)
            metadata.reflect()
            to_be_deleted = [metadata.tables[name] for name in metadata.tables]
            metadata.drop_all(engine, to_be_deleted)

        def _drop_views(schema, views):
            with engine.connect() as conn:
                for name in views:
                    conn.execute(f"DROP VIEW {schema}.{name};")

        _drop_tables(cls.schema)
        _drop_views(cls.schema, cls.views)

    @pytest.mark.parametrize("pool_type", POOL_TYPES)
    def test_introspection_of_tables_works_with(self, pool_type):
        expected = self.tables
        engine = create_engine(config.db.url, poolclass=pool_type)
        inspector = inspect(engine)
        tables = inspector.get_table_names(schema=self.schema)
        assert expected == tables

    @pytest.mark.parametrize("pool_type", POOL_TYPES)
    def test_introspection_of_views_works_with(self, pool_type):
        expected = self.views
        engine = create_engine(config.db.url, poolclass=pool_type)
        inspector = inspect(engine)
        tables = inspector.get_view_names(schema=self.schema)
        assert expected == tables
