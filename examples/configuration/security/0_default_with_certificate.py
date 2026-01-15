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
)

create_engine(url_object)
