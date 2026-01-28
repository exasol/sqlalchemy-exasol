from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)

from examples.config import (
    DEFAULT_SCHEMA_NAME,
    ENGINE,
    SQL_ALCHEMY,
)

# 1. Ensure that the schema exists
SQL_ALCHEMY.create_schema(engine=ENGINE, schema=DEFAULT_SCHEMA_NAME)

# 2. Use the schema to define the metadata_obj, which is used in the `Base` class
metadata_obj = MetaData(schema=DEFAULT_SCHEMA_NAME)


metadata = MetaData()

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
    Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE")),
)

# 4. Create all tables
with ENGINE.begin() as conn:
    metadata.create_all(conn)
