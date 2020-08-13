# -*- coding: UTF-8 -*-
import time

import pytest
from sqlalchemy.testing import fixtures, config
from sqlalchemy import MetaData, Table, Column, Integer


table_counts = [1,50,100]
column_counts = [3,30,300]

class LargeMetadataTest(fixtures.TablesTest):
    __backend__ = True


    def create_table_ddl(self, schema, name, column_count):
        table_template = "CREATE TABLE {schema}.{table} ({columns})"
        columns = ["column_column_%s int" % i for i in range(column_count)]
        columns_str = ",".join(columns)
        table_str = table_template.format(schema=schema, table=name, columns=columns_str)
        return table_str

    @classmethod
    def define_tables(cls, metadata):
        cls.schema = "LargeMetadataTest".upper()

    def get_table_name(self, table_count, column_count, i):
        return "table_%s_%s_table_%s" % (table_count, column_count, i)

    def test_reflect_table_object(self):
        for table_count in table_counts:
            for column_count in column_counts:
                with config.db.begin() as c:
                    try:
                        c.execute("DROP SCHEMA %s CASCADE" % self.schema)
                    except Exception as e:
                        print(e)
                        pass
                    c.execute("CREATE SCHEMA %s" % self.schema)
                    for i in range(table_count):
                        table_name=self.get_table_name(table_count,column_count,i)
                        table_ddl=self.create_table_ddl(self.schema,table_name,column_count)
                        c.execute(table_ddl)

                meta = MetaData(bind=config.db)
                table_name = self.get_table_name(table_count, column_count, 0)
                start = time.time()
                users_table = Table(table_name,meta,autoload=True, schema=self.schema)
                end = time.time()
                print("table load timer: attempt: 1, table_count: %s, column_count: %s, time: %s"%(table_count,column_count,
                      (end-start)))
                start = time.time()
                users_table = Table(table_name,meta,autoload=True, schema=self.schema)
                end = time.time()
                print("table load timer: attempt: 2, table_count: %s, column_count: %s, time: %s"%(table_count,column_count,
                      (end-start)))
                meta = None

    def test_reflect_metadata_object(self):
        for table_count in table_counts:
            for column_count in column_counts:
                with config.db.begin() as c:
                    try:
                        c.execute("DROP SCHEMA %s CASCADE" % self.schema)
                    except Exception as e:
                        print(e)
                        pass
                    c.execute("CREATE SCHEMA %s" % self.schema)
                    for i in range(table_count):
                        table_name=self.get_table_name(table_count,column_count,i)
                        table_ddl=self.create_table_ddl(self.schema,table_name,column_count)
                        c.execute(table_ddl)
                meta = MetaData(bind=config.db)
                start = time.time()
                meta.reflect()
                end = time.time()
                print("all tables (MetaData.reflect) load timer: table_count: %s, column_count: %s, time: %s"%(table_count,column_count,
                      (end-start)))
