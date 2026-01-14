from sqlalchemy import (
    URL,
    create_engine,
    text,
)

# These values come from the defaults of the Exasol Docker DB.
# Please adapt them for your safe-to-test DB use case.
url_object = URL.create(
    drivername="exa+websocket",
    username="sys",
    password="exasol",
    host="127.0.0.1",
    port=8563,
    # This value should only be used for non-productive use cases.
    # See https://exasol.github.io/sqlalchemy-exasol/master/user_guide/configuration/security.html
    # for more options for productive use cases.
    query={"FINGERPRINT": "nocertcheck"},
)

# All literal text should be passed through `text()` before execution.
sql_text = text("SELECT 42 FROM DUAL")

engine = create_engine(url_object)
with engine.connect() as con:
    result = con.execute(sql_text).fetchall()
print(f"QUERY RESULT: {result}")
