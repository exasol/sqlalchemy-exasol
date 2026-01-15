from sqlalchemy import (
    URL,
    create_engine,
    text,
)

url_object = URL.create(
    drivername="exa+websocket",
    username="sys",
    password="exasol",
    host="127.0.0.1",
    port=8563,
    # This is not recommended and should NEVER be used on production systems.
    query={"SSLCertificate": "SSL_VERIFY_NONE"},
)

create_engine(url_object)
# used in CI for verification

sql_text = text("SELECT 42 FROM DUAL")
engine = create_engine(url_object)
with engine.connect() as con:
    result = con.execute(sql_text).fetchall()
print(f"QUERY RESULT: {result}")
