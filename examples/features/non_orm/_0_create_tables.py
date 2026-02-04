from __future__ import annotations

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    text,
)

from examples.config import (
    DEFAULT_SCHEMA_NAME,
    ENGINE,
    SQL_ALCHEMY,
)

# For more information on table definitions, check out:
#    https://docs.sqlalchemy.org/en/21/tutorial/metadata.html

# 1. Ensure that the schema exists
SQL_ALCHEMY.create_schema(engine=ENGINE, schema=DEFAULT_SCHEMA_NAME)

# 2. Use the schema to define the metadata_obj
metadata = MetaData(schema=DEFAULT_SCHEMA_NAME)

# 3. Define tables
user_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("first_name", String(30), nullable=False),
    Column("last_name", String(30), nullable=False),
)

email_address_table = Table(
    "email_address",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email_address", String(100), nullable=False),
    Column("user_id", Integer, ForeignKey("user.id")),
)

# 4. Create all tables
with ENGINE.begin() as conn:
    metadata.create_all(conn)

# 5. Verify that the tables have been created
query = f"""
SELECT TABLE_NAME
FROM SYS.EXA_ALL_TABLES
WHERE TABLE_SCHEMA = '{DEFAULT_SCHEMA_NAME}'
ORDER BY TABLE_NAME
"""

with ENGINE.connect() as con:
    results = con.execute(text(query)).fetchall()

if __name__ == "__main__":
    print(f"Tables in schema={DEFAULT_SCHEMA_NAME}: {results}")
