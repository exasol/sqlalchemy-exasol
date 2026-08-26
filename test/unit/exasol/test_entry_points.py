from importlib.metadata import (
    EntryPoint,
    entry_points,
)

import pytest
from packaging.utils import canonicalize_name
from sqlalchemy import create_engine
from sqlalchemy.engine.default import DefaultDialect

from sqlalchemy_exasol.websocket import EXADialect_websocket

ENTRY_POINT_NAMES = ("exa", "exa.websocket")


def exasol_entry_points() -> dict[str, EntryPoint]:
    """Return this distribution's installed SQLAlchemy dialect entry points."""
    distribution_name = canonicalize_name("sqlalchemy-exasol")
    return {
        entry_point.name: entry_point
        for entry_point in entry_points(group="sqlalchemy.dialects")
        if entry_point.dist is not None
        and canonicalize_name(entry_point.dist.name) == distribution_name
    }


def test_dialect_entry_points_are_discoverable():
    discovered = exasol_entry_points()

    assert set(discovered) == set(ENTRY_POINT_NAMES)


@pytest.mark.parametrize("entry_point_name", ENTRY_POINT_NAMES)
def test_dialect_entry_points_have_superset_shape(entry_point_name):
    """Superset consumes the class returned directly by EntryPoint.load()."""
    dialect = exasol_entry_points()[entry_point_name].load()

    assert isinstance(dialect, type)
    assert issubclass(dialect, DefaultDialect)
    assert dialect.name == "exasol"
    assert dialect.driver == "exasol.driver.websocket.dbapi2"


@pytest.mark.parametrize(
    "url",
    (
        "exa://user:password@localhost:8563/schema",
        "exa+websocket://user:password@localhost:8563/schema",
    ),
)
def test_create_engine_uses_websocket_dialect_without_connecting(url):
    engine = create_engine(url)

    try:
        assert isinstance(engine.dialect, EXADialect_websocket)
    finally:
        engine.dispose()
