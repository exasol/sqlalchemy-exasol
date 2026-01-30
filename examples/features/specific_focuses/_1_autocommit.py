from sqlalchemy import text

from examples.config import (
    DEFAULT_SCHEMA_NAME,
    ENGINE,
    SQL_ALCHEMY,
)

# 0. Ensure that the schema exists
SQL_ALCHEMY.create_schema(engine=ENGINE, schema=DEFAULT_SCHEMA_NAME)

# 1. Data Definition Language (DDL)
TABLE_NAME = "HEX_LOOKUP"

create_hex_table = f"""
    CREATE OR REPLACE TABLE {DEFAULT_SCHEMA_NAME}.{TABLE_NAME} (
        id INTEGER IDENTITY PRIMARY KEY,
        hex_code CHAR(6) NOT NULL
    );
"""

with ENGINE.begin() as conn:
    conn.execute(text(create_hex_table))

# 2. Data Query Language (DQL)
query = f"""
SELECT *
FROM SYS.EXA_ALL_TABLES
WHERE TABLE_SCHEMA = '{DEFAULT_SCHEMA_NAME}'
AND TABLE_NAME = '{TABLE_NAME}'
"""

with ENGINE.connect() as con:
    results = con.execute(text(query)).fetchall()
    # con.commit() is never needed for DQL

print(f"Table search result: {results}")

# 3. Data Manipulation Language (DML)
hex_data = [{"hex_code": "FF5733"}, {"hex_code": "33FF57"}, {"hex_code": "3357FF"}]

insert_statement = (
    f"INSERT INTO {DEFAULT_SCHEMA_NAME}.{TABLE_NAME} (hex_code) VALUES (:hex_code)"
)
with ENGINE.begin() as conn:
    conn.execute(text(insert_statement), hex_data)
    # if `ENGINE.connect()` were used instead of `ENGINE.begin()` and "AUTOCOMMIT" were
    # disabled, you MUST include a `con.commit()` for the change to be persisted;
    # otherwise, no results will be found in #4

# 4. DQL
select_statement = f"SELECT * FROM {DEFAULT_SCHEMA_NAME}.{TABLE_NAME}"

with ENGINE.connect() as con:
    result = con.execute(text(select_statement)).fetchall()

    print(f"Number of entries: {len(result)}")
    for row in result:
        print(row)
