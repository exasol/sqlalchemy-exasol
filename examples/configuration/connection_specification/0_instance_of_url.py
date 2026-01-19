from sqlalchemy import (
    URL,
    create_engine,
)

url_object = URL.create(
    drivername="exa+websocket",
    username="sys",
    password="exasol",
    host="127.0.0.1",
    port=8563,
    # All parameters that are not keyword arguments for `URL.create` are in added
    # into the `query` dictionary.
    query={
        "AUTOCOMMIT": "y",
        "CONNECTIONLCALL": "en_US.UTF-8",
        # This should NEVER be used for production systems,
        # see "Disable Certificate Verification" in the User Guide.
        "FINGERPRINT": "nocertcheck",
    },
)

create_engine(url_object)
