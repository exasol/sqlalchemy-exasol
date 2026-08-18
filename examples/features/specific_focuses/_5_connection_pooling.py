import sqlalchemy

from examples.config import (
    SQL_ALCHEMY,
)

# 1. Create an engine using a connection pool
engine = SQL_ALCHEMY.create_engine(
    poolclass=sqlalchemy.QueuePool,
    pool_size=10,
    max_overflow=2,
    pool_recycle=3600,  # recycle connections after an hour
    pool_pre_ping=True,  # test connection liveness before use
)


# 2. Listen when a connection is checked out from the pool
def on_checkout(dbapi_conn, connection_rec, connection_proxy):
    print(f"checkout: {dbapi_conn}")


sqlalchemy.event.listen(engine, "checkout", on_checkout)

# 3. Create a connection and execute a statement
with engine.connect() as con:
    res = con.execute(sqlalchemy.text("SELECT 1")).fetchone()
    print(f'Result: "{res}"')
