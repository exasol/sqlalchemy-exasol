from sqlalchemy import create_engine

username = "sys"
password = "exasol"
host = "127.0.0.1"
port = "8563"
schema = "my_schema"
# All parameters, which are not keyword arguments for `URL.create`,
# should be specified in `query` and are of the form NAME=value
# The first parameter in the query is preceded by a `?`.
# Additional parameters are preceded by a `&`.
query = (
    "?AUTOCOMMIT=y"
    "&CONNECTIONLCALL=en_US.UTF-8"
    # This should NEVER be used for production systems,
    # see "Disable Certificate Verification" in the User Guide.
    "&FINGERPRINT=nocertcheck"
)

url_string = f"exa+websocket://{username}:{password}@{host}:{port}/{schema}{query}"

create_engine(url_string)
