"""Integration tests for SQLAlchemy-Exasol type round trips."""

import datetime as dt
from contextlib import contextmanager
from decimal import Decimal

import pytest
import sqlalchemy as sa
from sqlalchemy.testing import fixtures

NUMERIC_INPUTS = (
    pytest.param(42, id="integer"),
    pytest.param(42.5, id="float"),
    pytest.param(Decimal("42.5"), id="decimal"),
    pytest.param("42.5", id="string-encoded-float"),
)

TIMESTAMP_INPUTS = (
    pytest.param(dt.datetime(2026, 9, 11, 12, 34, 56, 123400), id="datetime"),
    pytest.param("2026-09-11 12:34:56.1234", id="string"),
)


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

    @contextmanager
    def create_table_with_ddl(self, engine, schema, column_type, ddl_type):
        """Create a table with explicit DDL when no native SQLAlchemy equivalent exists."""
        self.table = sa.Table(
            "test_type",
            sa.MetaData(),
            sa.Column("value", column_type),
            schema=schema,
        )
        with engine.begin() as connection:
            connection.exec_driver_sql(
                f'CREATE TABLE {schema}.test_type ("value" {ddl_type})'
            )

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
    @pytest.mark.parametrize(
        "input_value",
        (
            pytest.param(True, id="boolean"),
            pytest.param(1, id="integer"),
        ),
    )
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table(engine, schema, sa.Boolean):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, bool)
        assert result is True

    def test_round_trip_none(self, engine, schema):
        with self.create_table(engine, schema, sa.Boolean):
            self.insert_value(engine, None)
            result = self.select_value(engine)

        assert result is None

    def test_rejects_string_input(self, engine, schema):
        # Strings are rejected by SQLAlchemy's strict Boolean validation as our dialect
        # advertises native Boolean support (supports_native_boolean = True). So this
        # exception is raised before it reaches PyExasol.
        with self.create_table(engine, schema, sa.Boolean):
            with pytest.raises(sa.exc.StatementError) as error:
                self.insert_value(engine, "TRUE")

        assert isinstance(error.value.orig, TypeError)


class TestCharType(TypeRoundTrip):

    @pytest.mark.parametrize(
        "input_value",
        (
            pytest.param("xy", id="too_short"),
            pytest.param("xy" + " " * 3, id="correct-length"),
        ),
    )
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table(engine, schema, sa.CHAR(5)):
            self.insert_value(engine, input_value)
            actual = self.select_value(engine)

        assert isinstance(actual, str)
        assert actual == "xy" + " " * 3

    def test_rejects_too_long(self, engine, schema):
        with self.create_table(engine, schema, sa.CHAR(5)):
            with pytest.raises(sa.exc.DatabaseError):
                self.insert_value(engine, "x" * 6)


class TestDateType(TypeRoundTrip):
    @pytest.mark.parametrize(
        "input_value",
        (
            pytest.param(dt.date(2026, 9, 11), id="date"),
            pytest.param("2026-09-11", id="string"),
        ),
    )
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table(engine, schema, sa.Date):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, dt.date)
        assert result == dt.date(2026, 9, 11)


class TestDecimalType(TypeRoundTrip):
    @pytest.mark.parametrize(
        "input_value",
        NUMERIC_INPUTS,
    )
    def test_round_trip_decimal_scale_0(self, engine, schema, input_value):
        with self.create_table(engine, schema, sa.Numeric(18, 0)):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, Decimal)
        assert result == Decimal("42")

    @pytest.mark.parametrize(
        "input_value",
        NUMERIC_INPUTS,
    )
    def test_round_trip_decimal_scale_1(self, engine, schema, input_value):
        with self.create_table(engine, schema, sa.Numeric(18, 1)):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, Decimal)
        if isinstance(input_value, int):
            assert result == Decimal("42")
        else:
            assert result == Decimal("42.5")


class TestDoubleType(TypeRoundTrip):
    @pytest.mark.parametrize(
        "input_value",
        NUMERIC_INPUTS,
    )
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table(engine, schema, sa.Double):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, float)
        if isinstance(input_value, int):
            assert result == 42.0
        else:
            assert result == 42.5


class TestFloatType(TypeRoundTrip):
    @pytest.mark.parametrize(
        "input_value",
        NUMERIC_INPUTS,
    )
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table(engine, schema, sa.Float):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, float)
        if isinstance(input_value, int):
            assert result == 42.0
        else:
            assert result == 42.5


class TestIntegerType(TypeRoundTrip):
    @pytest.mark.parametrize(
        "input_value",
        NUMERIC_INPUTS,
    )
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table(engine, schema, sa.Integer):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, int)
        assert result == 42


class TestTimeType(TypeRoundTrip):
    # Exasol has no native TIME type. The dialect maps sa.Time to VARCHAR(16) in
    # EXATypeCompiler.visit_TIME() and uses EXATimestring in type_descriptor().
    @pytest.mark.parametrize(
        "input_value",
        (
            pytest.param(dt.time(12, 34, 56, 123456), id="time"),
            pytest.param("12:34:56.123456", id="string"),
        ),
    )
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table(engine, schema, sa.Time):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, str)
        assert result == "12:34:56.123456"


class TestTimestampType(TypeRoundTrip):
    @pytest.mark.parametrize(
        "input_value",
        TIMESTAMP_INPUTS,
    )
    def test_round_trip_datetime(self, engine, schema, input_value):
        with self.create_table(engine, schema, sa.DateTime):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, dt.datetime)
        assert result == dt.datetime(2026, 9, 11, 12, 34, 56, 123000)

    @pytest.mark.parametrize(
        "input_value",
        TIMESTAMP_INPUTS,
    )
    def test_round_trip_timestamp(self, engine, schema, input_value):
        # Explicit timestamp precision is currently discarded by the dialect;
        # EXATypeCompiler._timestamp() in sqlalchemy_exasol/base.py emits TIMESTAMP.
        with self.create_table(engine, schema, sa.TIMESTAMP):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, dt.datetime)
        # Exasol's default TIMESTAMP precision is 3 fractional digits, including
        # on versions >= 8.32.0. Version 8.32.0 added explicit TIMESTAMP(p)
        # precision; it did not change the precision of bare TIMESTAMP.
        # See https://docs.exasol.com/db/latest/sql_references/data_types/datatypedetails.htm
        expected = dt.datetime(2026, 9, 11, 12, 34, 56, 123000)
        assert result == expected

    @pytest.mark.parametrize(
        "input_value",
        TIMESTAMP_INPUTS,
    )
    def test_round_trip_timestamp_with_explicit_precision_3(
        self, engine, schema, input_value
    ):
        with self.create_table_with_ddl(engine, schema, sa.TIMESTAMP, "TIMESTAMP(3)"):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, dt.datetime)
        assert result == dt.datetime(2026, 9, 11, 12, 34, 56, 123000)


class TestVarcharType(TypeRoundTrip):
    @pytest.mark.parametrize(
        "input_value",
        (
            pytest.param("Exasol", id="shorter"),
            pytest.param("x" * 20, id="right-length"),
        ),
    )
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table(engine, schema, sa.String(20)):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, str)
        assert result == input_value

    def test_rejects_too_long(self, engine, schema):
        with self.create_table(engine, schema, sa.String(20)):
            with pytest.raises(sa.exc.DatabaseError):
                self.insert_value(engine, "x" * 21)
