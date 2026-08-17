import sqlalchemy

# 1. Create an engine using a connection pool
engine = sqlalchemy.create_engine(
    url,
    poolclass=sqlalchemy.QueuePool,
    pool_size=10,
    max_overflow=2,
    pool_recycle=3600,  # recycle connections after an hour
    pool_pre_ping=True,  # test connection liveness before use
)

# 2. Create and connection and execute a statement
with engine.connect() as con:
    res = con.excute(sqlalchemy.text("SELECT 1").fetchone()
    print(f'Result: "{res}"')
