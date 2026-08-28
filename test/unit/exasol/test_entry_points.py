"""Tests for the dialect entry points in the installed distribution metadata.

These tests intentionally inspect installed metadata rather than ``pyproject.toml``.
An editable install can retain stale entry-point metadata after ``pyproject.toml`` is
edited, so developers must reinstall the project before running this module.  That
tradeoff ensures the tests exercise the same metadata used by entry-point consumers.
"""

import subprocess
import sys
from importlib.metadata import (
    EntryPoint,
    entry_points,
)

import pytest
from packaging.utils import canonicalize_name
from sqlalchemy.engine.default import DefaultDialect

from sqlalchemy_exasol import base
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

    assert dialect is EXADialect_websocket
    assert isinstance(dialect, type)
    assert issubclass(dialect, DefaultDialect)
    assert dialect.name == "exasol"
    assert dialect.driver == "exasol.driver.websocket.dbapi2"


def test_bare_entry_point_matches_runtime_default():
    dialect = exasol_entry_points()["exa"].load()

    assert dialect is base.dialect


@pytest.mark.parametrize(
    ("entry_point_name", "url"),
    (
        ("exa", "exa://user:password@localhost:8563/schema"),
        (
            "exa.websocket",
            "exa+websocket://user:password@localhost:8563/schema",
        ),
    ),
)
def test_create_engine_uses_installed_websocket_dialect_without_connecting(
    entry_point_name, url
):
    """Use a clean interpreter so SQLAlchemy's registry cannot mask bad metadata."""
    code = f"""
from sqlalchemy import create_engine
from sqlalchemy.dialects import registry
from sqlalchemy_exasol.websocket import EXADialect_websocket

assert {entry_point_name!r} not in registry.impls
engine = create_engine({url!r})
try:
    assert type(engine.dialect) is EXADialect_websocket
finally:
    engine.dispose()
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
