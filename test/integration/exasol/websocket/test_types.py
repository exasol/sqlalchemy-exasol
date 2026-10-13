"""Integration tests for SQLAlchemy-Exasol type round trips."""

import datetime as dt
from contextlib import contextmanager
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.testing import fixtures


class TypeRoundTrip(fixtures.TestBase):
    table = None

    @contextmanager
    def create_table(self, engine, schema, column_type):
        self.table = sa.Table(
            "test_type",
            sa.MetaData(),
            sa.Column("value", column_type),
            schema=schema,
        )
        self.table.create(engine)

        try:
            yield
        finally:
            self.table.drop(engine)

    def insert_value(self, engine, value):
        with engine.begin() as connection:
            connection.execute(self.table.insert(), {"value": value})

    def select_value(self, engine):
        with engine.connect() as connection:
            return connection.execute(sa.select(self.table.c.value)).scalar_one()


class TestBooleanType(TypeRoundTrip):
    def test_round_trip(self, engine, schema):
        with self.create_table(engine, schema, sa.Boolean):
            expected = True
            self.insert_value(engine, expected)
            actual = self.select_value(engine)

            assert isinstance(actual, bool)
            assert actual is expected


class TestCharType(TypeRoundTrip):
    def test_round_trip(self, engine, schema):
        with self.create_table(engine, schema, sa.CHAR(5)):
            expected = "xy   "
            self.insert_value(engine, expected)
            actual = self.select_value(engine)

            assert isinstance(actual, str)
            assert actual == expected


class TestDateType(TypeRoundTrip):
    def test_round_trip(self, engine, schema):
        with self.create_table(engine, schema, sa.Date):
            expected = dt.date(2026, 9, 11)
            self.insert_value(engine, expected)
            actual = self.select_value(engine)

            assert isinstance(actual, dt.date)
            assert actual == expected


class TestDecimalType(TypeRoundTrip):
    def test_round_trip(self, engine, schema):
        with self.create_table(engine, schema, sa.Numeric(18, 2)):
            expected = Decimal("123.45")
            self.insert_value(engine, expected)
            actual = self.select_value(engine)

            assert isinstance(actual, Decimal)
            assert actual == expected


class TestFloatType(TypeRoundTrip):
    def test_round_trip(self, engine, schema):
        with self.create_table(engine, schema, sa.Float):
            expected = 1.25
            self.insert_value(engine, expected)
            actual = self.select_value(engine)

            assert isinstance(actual, float)
            assert actual == expected


class TestIntegerType(TypeRoundTrip):
    def test_round_trip(self, engine, schema):
        with self.create_table(engine, schema, sa.Integer):
            expected = 42
            self.insert_value(engine, expected)
            actual = self.select_value(engine)

            assert isinstance(actual, int)
            assert actual == expected


class TestTimeType(TypeRoundTrip):
    def test_round_trip(self, engine, schema):
        with self.create_table(engine, schema, sa.Time):
            value = dt.time(12, 34, 56, 123456)
            expected = "12:34:56.123456"
            self.insert_value(engine, value)
            actual = self.select_value(engine)

            assert isinstance(actual, str)
            assert actual == expected


class TestVarcharType(TypeRoundTrip):
    def test_round_trip(self, engine, schema):
        with self.create_table(engine, schema, sa.String(20)):
            expected = "Exasol"
            self.insert_value(engine, expected)
            actual = self.select_value(engine)

            assert isinstance(actual, str)
            assert actual == expected
