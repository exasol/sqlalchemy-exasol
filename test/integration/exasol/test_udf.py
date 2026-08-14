from inspect import cleandoc

from sqlalchemy import (
    create_engine,
    text,
)
from sqlalchemy.schema import (
    CreateSchema,
    DropSchema,
)
from sqlalchemy.testing import (
    config,
    fixtures,
)


class Udf(fixtures.TestBase):
    @classmethod
    def setup_class(cls):
        cls.schema = "test"
        with config.db.begin() as conn:
            conn.execute(CreateSchema(cls.schema))
            
    @classmethod
    def teardown_class(cls):
        with config.db.begin() as conn:
            conn.execute(DropSchema(cls.schema, cascade=True))

    def test_udf(self):
        engine = create_engine(config.db.url)
        UDF = cleandoc(f"""
            --/
            CREATE OR REPLACE PYTHON3 SCALAR SCRIPT
              "{self.schema}".UDF(
              "a" VARCHAR(200)
            ) EMITS (
              "result" VARCHAR(2000)
            ) AS
            def run(ctx):
                ctx.emit("Input: " + ctx.a)
            /
        """)
        with engine.connect() as con:
            con.execute(text(UDF))
            res = con.execute(text(f"SELECT "{self.schema}".UDF('abc')")).fetchone()
        assert res[0] == "Input: abc"
