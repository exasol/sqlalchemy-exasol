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
from sqlalchemy.sql.ddl import DropSchema

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
        return f"EmailAddress(id={self.id!r}, email_address={self.email_address!r})"


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


@pytest.fixture(scope="module")
def add_tables(engine):
    with engine.begin() as conn:
        conn.execute(CreateSchema(SCHEMA_NAME))
    Base.metadata.create_all(engine)
    yield
    with engine.begin() as conn:
        conn.execute(DropSchema(SCHEMA_NAME, cascade=True))


class TestGetLastRowID:
    @staticmethod
    def create_and_flush_users(session) -> list[User]:
        data = [
            {
                "first_name": "Lux",
                "last_name": "Noceda",
                "email_addresses": [
                    "fantasy4l!fe@hotmail.com",
                    "lux.noceda@hexside.com",
                ],
            }
        ]

        users = []
        for entry in data:
            u = User(first_name=entry["first_name"], last_name=entry["last_name"])
            u._pending_emails = entry["email_addresses"]
            users.append(u)

        session.add_all(users)
        session.flush()

        return users

    @staticmethod
    def create_email_addresses(users: list[User]) -> list[EmailAddress]:
        email_addresses = []
        for u in users:
            for email in u._pending_emails:
                email_addresses.append({"user_id": u.id, "email_address": email})
        return email_addresses

    def test_works_as_expected(self, add_tables, engine):
        with Session(engine) as session:
            users = self.create_and_flush_users(session)
            email_addresses = self.create_email_addresses(users)

            session.execute(insert(EmailAddress), email_addresses)
            session.commit()

    def test_returns_incorrect_value_to_raise_error(self, add_tables, engine):
        context_cls = engine.dialect.execution_ctx_cls

        with patch.object(context_cls, "get_lastrowid", return_value=999):
            with Session(engine) as session:
                users = self.create_and_flush_users(session)
                email_addresses = self.create_email_addresses(users)

                with pytest.raises(DBAPIError):
                    session.execute(insert(EmailAddress), email_addresses)
