from __future__ import annotations

from sqlalchemy import (
    Column,
    ForeignKey,
    MetaData,
    String,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from examples.config import (
    DEFAULT_SCHEMA_NAME,
    ENGINE,
    SQL_ALCHEMY,
)

# For more information on ORM table definition, check out:
#    https://docs.sqlalchemy.org/en/20/orm/quickstart.html#orm-quick-start

# 1. Ensure that the schema exists
SQL_ALCHEMY.create_schema(engine=ENGINE, schema=DEFAULT_SCHEMA_NAME)

# 2. Use the schema to define the metadata_obj, which is used in the `Base` class
metadata_obj = MetaData(schema=DEFAULT_SCHEMA_NAME)


class Base(DeclarativeBase):
    metadata = metadata_obj


# 3. Inherit from the `Base` class when defining your tables
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


# 4. Create all tables
Base.metadata.create_all(ENGINE)

# 5. Verify that the tables have been created
query = f"""
SELECT TABLE_NAME
FROM SYS.EXA_ALL_TABLES
WHERE TABLE_SCHEMA = '{DEFAULT_SCHEMA_NAME}'
ORDER BY TABLE_NAME
"""

with ENGINE.connect() as con:
    results = con.execute(text(query)).fetchall()

if __name__ == "__main__":
    print(f"Tables in schema={DEFAULT_SCHEMA_NAME}: {results}")
