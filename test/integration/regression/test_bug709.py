from __future__ import annotations

from unittest.mock import patch

import pytest
from sqlalchemy import (
    URL,
    Column,
    ForeignKey,
    MetaData,
    String,
    create_engine,
    insert,
)
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
)
from sqlalchemy.schema import (
    CreateSchema,
)

SCHEMA_NAME = "bug_709"
metadata_obj = MetaData(schema=SCHEMA_NAME)


class Base(DeclarativeBase):
    metadata = metadata_obj


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))
    # For relationship, the column type must use the class name, but the
    # `back_populates` uses the name of the table in the database.
    email_addresses: Mapped[list[EmailAddress]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def first_email(self) -> Column[str] | None:
        if self.email_addresses:
            return self.email_addresses[0].email_address
        return None

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, first_name={self.first_name!r}, last_name={self.last_name!r})"


class EmailAddress(Base):
    __tablename__ = "email_address"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    email_address = Column(String(255))

    user: Mapped[User] = relationship(back_populates="email_addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


@pytest.fixture(scope="module")
def engine():
    url_object = URL.create(
        drivername="exa+websocket",
        username="sys",
        password="exasol",
        host="127.0.0.1",
        port=8563,
        query={
            "AUTOCOMMIT": "y",
            "CONNECTIONLCALL": "en_US.UTF-8",
            "FINGERPRINT": "nocertcheck",
        },
    )
    return create_engine(url_object)


@pytest.fixture
def data():
    return [
        {
            "first_name": "Lux",
            "last_name": "Noceda",
            "email_addresses": ["fantasy4l!fe@hotmail.com", "lux.noceda@hexside.com"],
        }
    ]


@pytest.fixture(scope="module")
def add_tables(engine):
    with engine.begin() as conn:
        # Create schema once for the whole test suite
        conn.execute(CreateSchema(SCHEMA_NAME))
    Base.metadata.create_all(engine)


def test_lastrowid_works_without_error_for_linked_tables(add_tables, engine, data):
    with Session(engine) as session:
        user_objects = []
        for entry in data:
            u = User(first_name=entry["first_name"], last_name=entry["last_name"])
            u._pending_emails = entry["email_addresses"]
            user_objects.append(u)

        session.add_all(user_objects)
        session.flush()

        email_payload = []
        for u in user_objects:
            for email in u._pending_emails:
                email_payload.append({"user_id": u.id, "email_address": email})

        session.execute(insert(EmailAddress), email_payload)
        session.commit()


def test_lastrowid_gives_incorrect_value_to_raise_error(add_tables, engine, data):
    context_cls = engine.dialect.execution_ctx_cls

    with patch.object(context_cls, "get_lastrowid", return_value=999):
        with Session(engine) as session:
            user_objects = []
            for entry in data:
                u = User(first_name=entry["first_name"], last_name=entry["last_name"])
                u._pending_emails = entry["email_addresses"]
                user_objects.append(u)

            session.add_all(user_objects)
            session.flush()

            email_payload = []
            for u in user_objects:
                for email in u._pending_emails:
                    email_payload.append({"user_id": u.id, "email_address": email})

            with pytest.raises(DBAPIError):
                session.execute(insert(EmailAddress), email_payload)
