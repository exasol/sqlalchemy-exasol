"""Integration tests for websocket timestamp behavior."""

import datetime as dt

import pytest
import sqlalchemy as sa
from sqlalchemy.testing import fixtures


class TestTimestampRoundTrip(fixtures.TestBase):
    @pytest.mark.parametrize(
        "precision,fraction",
        [
            pytest.param(3, 123000, id="millisecond-precision"),
            pytest.param(6, 123456, id="full-microsecond-precision"),
            pytest.param(6, 1, id="microsecond-with-zero-padding"),
        ],
    )
    def test_typed_timestamp_preserves_server_fraction(
        self, pooled_engine, schema, precision, fraction
    ):
        # Setup: create and reflect a timestamp table with the requested precision.
        expected = dt.datetime(2026, 9, 11, 12, 34, 56, fraction)
        with pooled_engine.begin() as connection:
            # Before 8.32, TIMESTAMP(6) was an alias for millisecond precision.
            # Keep the millisecond regression on every supported server.
            # https://docs.exasol.com/db/latest/changelogs/13712.htm
            if precision > 3 and pooled_engine.dialect.server_version_info < (8, 32, 0):
                pytest.skip("Microsecond storage requires Exasol >= 8.32")
            connection.exec_driver_sql(
                f"CREATE TABLE {schema}.T (ID INT, TS TIMESTAMP({precision}))"
            )
        table = sa.Table(
            "t", sa.MetaData(), schema=schema.lower(), autoload_with=pooled_engine
        )

        # Action: insert one typed value, one NULL, and one independently seeded value.
        with pooled_engine.begin() as connection:
            connection.execute(
                table.insert(), [{"id": 1, "ts": expected}, {"id": 2, "ts": None}]
            )
            connection.exec_driver_sql(
                f"INSERT INTO {schema}.T VALUES (3, TIMESTAMP '{expected.isoformat(sep=' ')}')"
            )

        # Assert: both raw and reflected reads preserve the expected timestamp values.
        with pooled_engine.connect() as connection:
            raw = connection.exec_driver_sql(
                f"SELECT TS FROM {schema}.T WHERE ID=1"
            ).scalar_one()
            assert dt.datetime.fromisoformat(raw) == expected
            assert connection.execute(
                sa.select(table.c.ts).order_by(table.c.id)
            ).scalars().all() == [expected, None, expected]
