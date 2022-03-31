"""This module contains various regression test for issues which have been fixed in the past"""
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, schema
from sqlalchemy.testing import fixtures
from sqlalchemy.testing.fixtures import config


class RegressionTest(fixtures.TestBase):
    def setUp(self):
        self.table_name = "my_table"
        self.tenant_schema_name = "tenant_schema"
        engine = config.db
        with config.db.connect() as conn:
            conn.execute(schema.CreateSchema(self.tenant_schema_name))
            metadata = MetaData()
            Table(
                self.table_name,
                metadata,
                Column("id", Integer, primary_key=True),
                Column("name", String(1000), nullable=False),
                schema=self.tenant_schema_name,
            )
            metadata.create_all(engine)

    def tearDown(self):
        with config.db.connect() as conn:
            conn.execute(schema.DropSchema(self.tenant_schema_name, cascade=True))

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
