# This is nearly identical to 0_test_first_connection.py, but here we use the
# `ENGINE`. This is an important step before continuing with other examples.

from sqlalchemy import (
    text,
)

from examples.config import ENGINE

"""
If `Engine.connect()` fails, please double-check the credentials
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

# All literal text should be passed through `text()` before execution.
sql_text = text("SELECT 42 FROM DUAL")

with ENGINE.connect() as con:
    result = con.execute(sql_text).fetchall()
print(f"QUERY RESULT: {result}")
