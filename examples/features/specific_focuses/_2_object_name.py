from sqlalchemy import (
    CHAR,
    Column,
    Integer,
    MetaData,
    Table,
    text,
)

from examples.config import (
    DEFAULT_SCHEMA_NAME,
    ENGINE,
    SQL_ALCHEMY,
)

# 0. Ensure that the schema exists
SQL_ALCHEMY.create_schema(engine=ENGINE, schema=DEFAULT_SCHEMA_NAME)
metadata = MetaData(schema=DEFAULT_SCHEMA_NAME)

# 1. Create the table
table_name_lower = "hex_lookup"

hex_table = Table(
    # table_name_lower.upper() also would work
    table_name_lower.lower(),
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("hex_code", CHAR(6), nullable=False),
)

with ENGINE.begin() as conn:
    metadata.create_all(conn)

# 2. Select with Fully Prepared Raw SQL Statement

# Here only table_name_lower.upper(), etc. would work,
# as the internal values are saved in uppercase.
query = f"""
SELECT *
FROM SYS.EXA_ALL_TABLES
WHERE TABLE_SCHEMA = '{DEFAULT_SCHEMA_NAME.upper()}'
AND TABLE_NAME = '{table_name_lower.upper()}'
"""

with ENGINE.connect() as con:
    results = con.execute(text(query)).fetchall()

print(results)
