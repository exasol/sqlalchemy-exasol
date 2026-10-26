"""Integration tests for SQLAlchemy-Exasol type round trips."""

import datetime as dt
from contextlib import contextmanager
from decimal import Decimal

import pyexasol
import pytest
from packaging.version import Version
from pyexasol import ExaTimeDelta
from sqlalchemy import (
    CHAR,
    TIMESTAMP,
    Boolean,
    Column,
    Date,
    DateTime,
    Double,
    Float,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Time,
    select,
)
from sqlalchemy.exc import (
    DatabaseError,
    StatementError,
)
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

NULLABLE_TYPES = (
    pytest.param(Boolean, id="boolean"),
    pytest.param(CHAR(5), id="char"),
    pytest.param(Date, id="date"),
    pytest.param(Numeric(18, 1), id="numeric"),
    pytest.param(Double, id="double"),
    pytest.param(Float, id="float"),
    pytest.param(Integer, id="integer"),
    pytest.param(Time, id="time"),
    pytest.param(DateTime, id="datetime"),
    pytest.param(TIMESTAMP, id="timestamp"),
    pytest.param(String(20), id="string"),
)


class TypeRoundTrip(fixtures.TestBase):
    table = None

    @contextmanager
    def create_table(self, engine, schema, column_type):
        self.table = Table(
            "test_type",
            MetaData(),
            Column("value", column_type),
            schema=schema,
        )
        self.table.create(engine)

        try:
            yield
        finally:
            self.table.drop(engine)

    @contextmanager
    def create_table_with_ddl(self, engine, schema, ddl_type):
        """Create a table with explicit DDL."""
        self.table = Table(
            "test_type",
            MetaData(),
            # String is a placeholder as these cases have no native
            # SQLAlchemy equivalent.
            Column("value", String()),
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
            return connection.execute(select(self.table.c.value)).scalar_one()


class TestNullType(TypeRoundTrip):
    @pytest.mark.parametrize("column_type", NULLABLE_TYPES)
    def test_round_trip_none(self, engine, schema, column_type):
        with self.create_table(engine, schema, column_type):
            self.insert_value(engine, None)
            result = self.select_value(engine)

        assert result is None


class TestBooleanType(TypeRoundTrip):
    @pytest.mark.parametrize(
        "input_value",
        (
            pytest.param(True, id="boolean"),
            pytest.param(1, id="integer"),
        ),
    )
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table(engine, schema, Boolean):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, bool)
        assert result is True

    def test_rejects_string_input(self, engine, schema):
        # Strings are rejected by SQLAlchemy's strict Boolean validation as our dialect
        # advertises native Boolean support (supports_native_boolean = True). So this
        # exception is raised before it reaches PyExasol.
        with self.create_table(engine, schema, Boolean):
            with pytest.raises(StatementError) as error:
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
        with self.create_table(engine, schema, CHAR(5)):
            self.insert_value(engine, input_value)
            actual = self.select_value(engine)

        assert isinstance(actual, str)
        assert actual == "xy" + " " * 3

    def test_rejects_too_long(self, engine, schema):
        with self.create_table(engine, schema, CHAR(5)):
            with pytest.raises(DatabaseError):
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
        with self.create_table(engine, schema, Date):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, dt.date)
        assert result == dt.date(2026, 9, 11)


class TestDecimalType(TypeRoundTrip):
    def test_precision_above_exasol_limit_rejected(self, engine, schema):
        # Companion to TrueDivTest.test_truediv_divisor in
        # test/integration/sqlalchemy/test_suite.py: if this limit changes, update
        # those cases too.
        with pytest.raises(DatabaseError):
            with self.create_table(engine, schema, Numeric(37, 0)):
                pass

    @pytest.mark.parametrize(
        "input_value",
        NUMERIC_INPUTS,
    )
    def test_round_trip_numeric_scale_0(self, engine, schema, input_value):
        with self.create_table(engine, schema, Numeric(18, 0)):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, Decimal)
        assert result == Decimal("42")

    def test_round_trip_decimal_scale_0(self, engine, schema):
        with self.create_table_with_ddl(engine, schema, "DECIMAL(18, 0)"):
            self.insert_value(engine, 42)
            result = self.select_value(engine)

        assert isinstance(result, int)
        assert result == 42

    @pytest.mark.parametrize(
        "input_value",
        NUMERIC_INPUTS,
    )
    def test_round_trip_numeric_scale_1(self, engine, schema, input_value):
        with self.create_table(engine, schema, Numeric(18, 1)):
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
        with self.create_table(engine, schema, Double):
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
        with self.create_table(engine, schema, Float):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, float)
        if isinstance(input_value, int):
            assert result == 42.0
        else:
            assert result == 42.5


class TestGeometryType(TypeRoundTrip):
    # Exasol GEOMETRY has no first-class SQLAlchemy-Exasol type.
    def test_round_trip(self, engine, schema):
        value = "LINESTRING (10 20, 30 40)"
        # String is a placeholder; the DDL creates the actual GEOMETRY column.
        with self.create_table_with_ddl(engine, schema, "GEOMETRY"):
            self.insert_value(engine, value)
            result = self.select_value(engine)

        assert isinstance(result, str)
        assert result == value


class TestHashType(TypeRoundTrip):
    # Exasol HASHTYPE has no first-class SQLAlchemy-Exasol type.
    def test_round_trip(self, engine, schema):
        if Version(pyexasol.__version__) < Version("3.0.0"):
            # PyExasol versions before 3.0.0 do not map HASHTYPE in the
            # WebSocket cursor metadata, causing a KeyError during SELECT.
            pytest.xfail("HASHTYPE metadata mapping requires PyExasol >= 3.0.0")

        value = "6ba7b8109dad11d180b400c04fd430c8"
        with self.create_table_with_ddl(engine, schema, "HASHTYPE(16 BYTE)"):
            self.insert_value(engine, value)
            result = self.select_value(engine)

        assert isinstance(result, str)
        assert result == value


class TestIntervalDaySecondType(TypeRoundTrip):
    # Exasol INTERVAL has no first-class SQLAlchemy-Exasol type.
    @pytest.mark.parametrize(
        "input_value",
        (
            pytest.param("+000000003 04:05:06.654", id="string"),
            pytest.param(
                dt.timedelta(
                    days=3,
                    hours=4,
                    minutes=5,
                    seconds=6,
                    microseconds=654000,
                ),
                id="timedelta",
            ),
            pytest.param(
                pyexasol.ExaTimeDelta(
                    days=3,
                    hours=4,
                    minutes=5,
                    seconds=6,
                    microseconds=654000,
                ),
                id="exa-timedelta",
            ),
        ),
    )
    def test_round_trip(self, engine, schema, input_value):
        if not isinstance(input_value, str):
            pytest.xfail(
                "PyExasol does not support interval input values; "
                "see https://github.com/exasol/pyexasol/issues/428"
            )

        with self.create_table_with_ddl(engine, schema, "INTERVAL DAY(9) TO SECOND(6)"):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        if Version(pyexasol.__version__) < Version("3.0.0"):
            # PyExasol before 3.0.0 returns serialized interval values.
            assert isinstance(result, str)
            assert result == "+000000003 04:05:06.654000"
        else:
            # PyExasol 3.0.0 returns day-to-second intervals as ExaTimeDelta.
            assert isinstance(result, ExaTimeDelta)
            assert result == dt.timedelta(
                days=3,
                hours=4,
                minutes=5,
                seconds=6,
                microseconds=654000,
            )


class TestIntervalYearMonthType(TypeRoundTrip):
    # Exasol INTERVAL has no first-class SQLAlchemy-Exasol type.
    def test_round_trip(self, engine, schema):
        value = "+0001-11"
        with self.create_table_with_ddl(engine, schema, "INTERVAL YEAR(4) TO MONTH"):
            self.insert_value(engine, value)
            result = self.select_value(engine)

        assert isinstance(result, str)
        assert result == value


class TestIntegerType(TypeRoundTrip):
    @pytest.mark.parametrize(
        "input_value",
        NUMERIC_INPUTS,
    )
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table(engine, schema, Integer):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, int)
        assert result == 42


class TestTimeType(TypeRoundTrip):
    # Exasol has no native TIME type. The dialect maps Time to VARCHAR(16) in
    # EXATypeCompiler.visit_TIME() and uses EXATimestring in type_descriptor().
    @pytest.mark.parametrize(
        "input_value",
        (
            pytest.param(dt.time(12, 34, 56, 123456), id="time"),
            pytest.param("12:34:56.123456", id="string"),
        ),
    )
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table(engine, schema, Time):
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
        with self.create_table(engine, schema, DateTime):
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
        with self.create_table(engine, schema, TIMESTAMP):
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
        with self.create_table_with_ddl(engine, schema, "TIMESTAMP(3)"):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, dt.datetime)
        assert result == dt.datetime(2026, 9, 11, 12, 34, 56, 123000)

    @pytest.mark.parametrize(
        "fraction",
        [
            pytest.param(123456, id="full-microsecond-precision"),
            pytest.param(1, id="microsecond-with-zero-padding"),
        ],
    )
    def test_round_trip_timestamp_with_explicit_precision_6(
        self, engine, schema, fraction
    ):
        # In Exasol version <= 8.32.0, TIMESTAMP(6) was an alias for millisecond precision.
        # Thus, it will not appropriately work for this test.
        # https://docs.exasol.com/db/latest/changelogs/13712.htm
        if engine.dialect.server_version_info <= (8, 32, 0):
            pytest.xfail("Microsecond storage requires Exasol > 8.32")

        expected = dt.datetime(2026, 9, 11, 12, 34, 56, fraction)
        with self.create_table_with_ddl(engine, schema, "TIMESTAMP(6)"):
            self.insert_value(engine, expected)
            result = self.select_value(engine)

        assert isinstance(result, dt.datetime)
        assert result == expected


class TestTimestampLocalTimeZoneType(TypeRoundTrip):
    # Exasol TIMESTAMP WITH LOCAL TIME ZONE has no first-class SQLAlchemy-Exasol type.
    @pytest.mark.parametrize("input_value", TIMESTAMP_INPUTS)
    def test_round_trip(self, engine, schema, input_value):
        with self.create_table_with_ddl(
            engine, schema, "TIMESTAMP WITH LOCAL TIME ZONE"
        ):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        if Version(pyexasol.__version__) < Version("3.0.0"):
            assert isinstance(result, str)
            assert result == "2026-09-11 12:34:56.123000"
        else:
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
        with self.create_table(engine, schema, String(20)):
            self.insert_value(engine, input_value)
            result = self.select_value(engine)

        assert isinstance(result, str)
        assert result == input_value

    def test_rejects_too_long(self, engine, schema):
        with self.create_table(engine, schema, String(20)):
            with pytest.raises(DatabaseError):
                self.insert_value(engine, "x" * 21)
