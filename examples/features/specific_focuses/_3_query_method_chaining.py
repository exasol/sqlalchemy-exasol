from sqlalchemy import (
    CHAR,
    Column,
    Integer,
    MetaData,
    Table,
    desc,
    insert,
    select,
)

from examples.config import (
    DEFAULT_SCHEMA_NAME,
    ENGINE,
    SQL_ALCHEMY,
)

# 1. Ensure schema exists and define Table metadata
SQL_ALCHEMY.create_schema(engine=ENGINE, schema=DEFAULT_SCHEMA_NAME)
metadata_obj = MetaData(schema=DEFAULT_SCHEMA_NAME)

# 2. Create the table
hex_lookup = Table(
    "hex_lookup",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("hex_code", CHAR(6), nullable=False),
)
metadata_obj.create_all(ENGINE)

# 2. Insert data
hex_data = [{"hex_code": "FF5733"}, {"hex_code": "33FF57"}, {"hex_code": "3357FF"}]

with ENGINE.begin() as conn:
    conn.execute(insert(hex_lookup), hex_data)

# 3. Query method chaining
# Successive calls return a new Select object with the added clauses
stmt = (
    select(hex_lookup)
    .where(hex_lookup.c.hex_code.like("33%"))  # Using .c (columns) attribute
    .order_by(desc(hex_lookup.c.id))  # Chain ordering
)

with ENGINE.connect() as conn:
    results = conn.execute(stmt).fetchall()

print(f"Number of entries: {len(results)}")
for row in results:
    print(f"ID: {row.id}, Hex: {row.hex_code}")
