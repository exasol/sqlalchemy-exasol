import datetime

import pytest
from sqlalchemy import types as sqltypes

from sqlalchemy_exasol import (
    base,
    websocket,
)


@pytest.fixture()
def dialect():
    return base.EXADialect()


def test_type_descriptor_preserves_super_behavior_for_non_datetime(dialect):
    """For non-DateTime types, the override should behave like the base implementation."""
    # Compare to calling the parent class implementation directly.
    # This makes the test robust even if super() adapts types via colspecs.
    base_td = super(base.EXADialect, dialect).type_descriptor(sqltypes.Integer())
    td = dialect.type_descriptor(sqltypes.Integer())

    assert type(td) is type(base_td)


@pytest.fixture()
def websocket_dialect():
    return websocket.EXADialect_websocket()


def test_websocket_datetime_bind_processor_returns_none_for_none(websocket_dialect):
    processor = websocket.DateTime().bind_processor(websocket_dialect)

    assert processor(None) is None


def test_websocket_datetime_bind_processor_formats_python_datetime(
    websocket_dialect,
):
    processor = websocket.DateTime().bind_processor(websocket_dialect)
    value = datetime.datetime(2026, 1, 28, 12, 34, 56, 123456)

    assert processor(value) == "2026-01-28 12:34:56.123456"


def test_websocket_datetime_bind_processor_delegates_non_datetime_to_super_processor(
    monkeypatch, websocket_dialect
):
    seen = []

    def fake_super_bind_processor(self, dialect):
        def process(value):
            seen.append((dialect, value))
            return f"super:{value}"

        return process

    monkeypatch.setattr(sqltypes.DATETIME, "bind_processor", fake_super_bind_processor)

    processor = websocket.DateTime().bind_processor(websocket_dialect)

    assert processor("already-serialized") == "super:already-serialized"
    assert seen == [(websocket_dialect, "already-serialized")]


def test_websocket_datetime_bind_processor_returns_value_when_super_processor_missing(
    monkeypatch, websocket_dialect
):
    monkeypatch.setattr(sqltypes.DATETIME, "bind_processor", lambda self, dialect: None)

    processor = websocket.DateTime().bind_processor(websocket_dialect)

    assert processor("already-serialized") == "already-serialized"
