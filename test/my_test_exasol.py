# -*- coding: UTF-8 -*-
import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, Date, DateTime
from sqlalchemy import or_, select, literal_column
from sqlalchemy import testing, inspect
from sqlalchemy.schema import DropConstraint, AddConstraint
from sqlalchemy.testing import fixtures, config

from sqlalchemy_exasol.base import EXAExecutionContext
from sqlalchemy_exasol.constraints import DistributeByConstraint
from sqlalchemy_exasol.merge import merge
from sqlalchemy_exasol.util import raw_sql



class ConstraintsTest(fixtures.TablesTest):
    __backend__ = True

    def test_alter_table_distribute_by(self):
        for table in config.db.table_names():
            print("TABLE",table)
        insp = inspect(config.db)
        for schema in insp.get_schema_names():
            print("SCHEMA_engine",schema)
        c=config.db.connect()
        insp = inspect(c)
        for schema in insp.get_schema_names():
            print("SCHEMA_conn",schema)
        for view in insp.get_view_names():
            print("VIEW_conn",view)
            print(insp.get_view_definition(view))
        print("Columns for table",insp.get_table_names()[0])
        for column in insp.get_columns(table_name=insp.get_table_names()[0]):
            print("COLUMN",column)
        config.db.execute("DROP table fk_test")
        config.db.execute("CREATE OR REPLACE TABLE pk_test ( id1 int, id2 int, constraint pk_name_test  primary key (id1,id2))")
        print("pk",insp.get_pk_constraint("pk_test"))
     
        config.db.execute("CREATE OR REPLACE TABLE fk_test ( pk int, id1 int, id2 int, constraint fk_name_test  foreign key (id1,id2) references pk_test)")
        config.db.execute("commit")
        print("fk",insp.get_foreign_keys("fk_test"))
