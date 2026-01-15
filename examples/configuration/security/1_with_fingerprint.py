from sqlalchemy import (
    URL,
    create_engine,
)

fingerprint = "4B48CA613ACD27D4051673801538BAE504DB6F74B89D7752F19E6CD60E0D4EBC"

url_object = URL.create(
    drivername="exa+websocket",
    username="sys",
    password="exasol",
    host="127.0.0.1",
    port=8563,
    query={"FINGERPRINT": fingerprint},
)

create_engine(url_object)
