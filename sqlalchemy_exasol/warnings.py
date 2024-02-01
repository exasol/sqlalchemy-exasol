class SqlaExasolWarning(UserWarning):
    """Base class for all warnings emited by sqlalchemy_exasol."""


class SqlaExasolDeprecationWarning(SqlaExasolWarning, DeprecationWarning):
    """Warning class for features that will be removed in future versions."""
