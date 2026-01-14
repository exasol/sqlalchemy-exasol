# This is nearly identical to 0_create_and_test_connection.py, but here we use the
# `CONNECTION_CONFIG`. This is an important step before continuing with other examples.

from sqlalchemy import (
    URL,
    create_engine,
    text,
)

from examples.config import CONNECTION_CONFIG

"""
If `engine.connect()` fails, please double-check the credentials
you either put into `CONNECTION_CONFIG` or provided by setting environment variables (i.e
EXA_HOST, ...).

If you get an error message matching:
    Could not connect to Exasol: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify
    failed: self-signed certificate in certificate chain (_ssl.c:1004)

then, you need to provide the fingerprint or certificate to properly connect to your DB,
as described on:
- https://exasol.github.io/sqlalchemy-exasol/master/user_guide/configuration/security.html

You can set this either with the environment variable `EXA_QUERY` or by
modifying `CONNECTION_CONFIG.query`.
"""

url_object = URL.create(
    drivername="exa+websocket",
    username=CONNECTION_CONFIG.username,
    password=CONNECTION_CONFIG.password.get_secret_value(),
    host=CONNECTION_CONFIG.host,
    port=CONNECTION_CONFIG.port,
    database=CONNECTION_CONFIG.database,
    query=CONNECTION_CONFIG.query,
)

engine = create_engine(url_object)
# All literal text should be passed through `text()` before execution
sql_text = text("SELECT 42 FROM DUAL")

with engine.connect() as con:
    result = con.execute(sql_text).fetchall()
print(f"QUERY RESULT: {result}")
