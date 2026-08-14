from inspect import cleandoc

from sqlalchemy import (
    create_engine,
    text,
)
from sqlalchemy.testing import (
    config,
    fixtures,
)


class Udf(fixtures.TestBase):
    @classmethod
    def setup_class(cls):
        cls.schema = "test"

    @classmethod
    def teardown_class(cls):
        with config.db.begin() as con:
            con.execute(text("DROP SCRIPT UDF"))

    def test_udf(self):
        from sqlalchemy import create_engine, text

        engine = create_engine(config.db.url)
        UDF = cleandoc("""
            --/
            CREATE OR REPLACE PYTHON3 SCALAR SCRIPT
              UDF(
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
            res = con.execute(text("SELECT UDF('abc')")).fetchone()
        assert res[0] == "Input: abc"
