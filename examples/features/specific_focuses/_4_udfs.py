from inspect import cleandoc

from sqlalchemy import text

from examples.config import (
    DEFAULT_SCHEMA_NAME,
    ENGINE,
    SQL_ALCHEMY,
)

# 1. Ensure schema exists
SQL_ALCHEMY.create_schema(engine=ENGINE, schema=DEFAULT_SCHEMA_NAME)

# 2. Define the UDF
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

# 3. Create and execute the UDF
with ENGINE.connect() as conn:
    conn.execute(text(f"OPEN SCHEMA {DEFAULT_SCHEMA_NAME}"))
    conn.execute(text(UDF))
    res = conn.execute(text("SELECT UDF('abc')")).fetchone()
    print(f'Result: "{res}"')
