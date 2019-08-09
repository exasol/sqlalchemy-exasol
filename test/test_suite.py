# import all SQLAlchemy tests for this dialect
from sqlalchemy.testing.suite import *  # noqa: F403, F401

from sqlalchemy.testing.suite import CompoundSelectTest as _CompoundSelectTest


class CompoundSelectTest(_CompoundSelectTest):

    """ Skip this test as EXASOL does not allow EXISTS or IN predicates
        as part of the select list. Skipping is implemented by redefining
        the method as proposed by SQLAlchemy docs for new dialects."""
    def test_null_in_empty_set_is_false(self):
        return
