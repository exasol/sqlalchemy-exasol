"""Tests for the websocket dialect's custom DateTime type."""

import datetime
import time

import pytest
from sqlalchemy import DateTime


@pytest.fixture
def datetime_processor(uninitialized_engine):
    return (
        DateTime()
        .dialect_impl(uninitialized_engine.dialect)
        .result_processor(uninitialized_engine.dialect, None)
    )


@pytest.mark.parametrize(
    "text,expected",
    [
        pytest.param(
            "2026-09-11 12:34:56",
            datetime.datetime(2026, 9, 11, 12, 34, 56),
            id="no-fraction",
        ),
        pytest.param(
            "2026-09-11 12:34:56.1",
            datetime.datetime(2026, 9, 11, 12, 34, 56, 100000),
            id="one-digit-fraction-is-padded",
        ),
        pytest.param(
            "2026-09-11 12:34:56.123456",
            datetime.datetime(2026, 9, 11, 12, 34, 56, 123456),
            id="full-microsecond-precision",
        ),
        pytest.param(None, None, id="null-stays-null"),
        pytest.param(
            datetime.datetime(2026, 1, 1, 0, 0, 0, 123456),
            datetime.datetime(2026, 1, 1, 0, 0, 0, 123456),
            id="datetime-stays-unchanged",
        ),
    ],
)
def test_datetime_result(datetime_processor, text, expected):
    assert datetime_processor(text) == expected


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("invalid", id="not-a-datetime"),
        pytest.param("2024-02-30 00:00:00", id="invalid-calendar-date"),
        pytest.param("2026-09-11 12:34:56.1234567", id="too-many-fraction-digits"),
    ],
)
def test_datetime_invalid(datetime_processor, value):
    with pytest.raises(ValueError):
        datetime_processor(value)


@pytest.fixture
def timezone_datetime_processor(uninitialized_engine, monkeypatch):
    with monkeypatch.context() as timezone_patch:
        # A nonexistent local wall time must not be normalized through mktime.
        timezone_patch.setenv("TZ", "EST5EDT,M3.2.0,M11.1.0")
        time.tzset()
        try:
            yield DateTime().dialect_impl(
                uninitialized_engine.dialect
            ).result_processor(uninitialized_engine.dialect, None)
        finally:
            # tzset() reads TZ once; refresh it after monkeypatch restores TZ.
            timezone_patch.undo()
            time.tzset()


@pytest.mark.skipif(
    not hasattr(time, "tzset"),
    reason="requires Unix/Linux time.tzset support; unavailable on Windows",
)
def test_datetime_is_not_interpreted_in_local_timezone(timezone_datetime_processor):
    assert timezone_datetime_processor(
        "2026-03-08 02:30:00.123456"
    ) == datetime.datetime(2026, 3, 8, 2, 30, 0, 123456)
