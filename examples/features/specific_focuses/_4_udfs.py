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
UDF = cleandoc(f"""
    --/
    CREATE OR REPLACE PYTHON3 SCALAR SCRIPT
      "{DEFAULT_SCHEMA_NAME}".UDF(
      "a" VARCHAR(200)
    ) EMITS (
      "result" VARCHAR(2000)
    ) AS
    def run(ctx):
        ctx.emit("Input: " + ctx.a)
    /
""")

# 3. Execute the UDF
with ENGINE.connect() as conn:
    conn.execute(text(UDF))
    res = conn.execute(text(f"SELECT "{DEFAULT_SCHEMA_NAME}".UDF('abc')")).fetchone()
    print(f'Result: "{res[0]}"')
