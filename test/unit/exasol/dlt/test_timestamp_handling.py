import pytest
from sqlalchemy import types as sqltypes

from sqlalchemy_exasol import base


@pytest.fixture()
def dialect():
    return base.EXADialect()


def test_type_descriptor_wraps_datetime(dialect):
    """DateTime should be wrapped so pyexasol gets clean Python serialization."""
    td = dialect.type_descriptor(sqltypes.DateTime())
    assert isinstance(td, base.EXATimestamp)


def test_type_descriptor_wraps_timestamp_subclasses(dialect):
    """TIMESTAMP is a DateTime subclass in SQLAlchemy, so it should also wrap."""
    td = dialect.type_descriptor(sqltypes.TIMESTAMP())
    assert isinstance(td, base.EXATimestamp)


def test_type_descriptor_does_not_wrap_non_datetime(dialect):
    """Non-DateTime types should not be wrapped."""
    td = dialect.type_descriptor(sqltypes.Integer())
    assert not isinstance(td, base.EXATimestamp)
    # sanity: still a SQLAlchemy type object
    assert isinstance(td, sqltypes.TypeEngine)


def test_type_descriptor_preserves_super_behavior_for_non_datetime(dialect):
    """For non-DateTime types, the override should behave like the base implementation."""
    # Compare to calling the parent class implementation directly.
    # This makes the test robust even if super() adapts types via colspecs.
    base_td = super(base.EXADialect, dialect).type_descriptor(sqltypes.Integer())
    td = dialect.type_descriptor(sqltypes.Integer())

    assert type(td) is type(base_td)
