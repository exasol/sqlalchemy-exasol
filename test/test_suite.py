# import all SQLAlchemy tests for this dialect
import pytest
from sqlalchemy.testing.suite import *  # noqa: F403, F401

from sqlalchemy.testing.suite import CompoundSelectTest \
    as _CompoundSelectTest
from sqlalchemy.testing.suite import ExpandingBoundInTest \
    as _ExpandingBoundInTest
from sqlalchemy.testing.suite import NumericTest \
    as _NumericTest
from sqlalchemy.testing.suite import QuotedNameArgumentTest \
    as _QuotedNameArgumentTest


class CompoundSelectTest(_CompoundSelectTest):

    """ Skip this test as EXASOL does not allow EXISTS or IN predicates
        as part of the select list. Skipping is implemented by redefining
        the method as proposed by SQLAlchemy docs for new dialects."""
    def test_null_in_empty_set_is_false(self):
        return


class ExpandingBoundInTest(_ExpandingBoundInTest):

    """ Skip this test as EXASOL does not allow EXISTS or IN predicates
        as part of the select list. Skipping is implemented by redefining
        the method as proposed by SQLAlchemy docs for new dialects."""
    def test_null_in_empty_set_is_false(self):
        return


class NumericTest(_NumericTest):

    """ FIXME: test skipped to allow upgrading to SQLAlchemy 1.3.x due
        to vulnerability in 1.2.x. Need to understand reason for this.
        Hypothesis is that the data type is not correctly coerced between
        EXASOL and pyodbc."""
    def test_decimal_coerce_round_trip(self):
        return


class QuotedNameArgumentTest(_QuotedNameArgumentTest):

    """ This suite was added to SQLAlchemy 1.3.19 on July 2020 to address
        issues in other dialects related to object names that contain quotes 
        and double quotes. Since this feature is not relevant to the 
        Exasol dialect, the entire suite will be skipped. More info on fix:
        https://github.com/sqlalchemy/sqlalchemy/issues/5456 """
    @pytest.mark.skip()
    def test_get_table_options(self, name):
        return

    @pytest.mark.skip()
    def test_get_view_definition(self, name):
        return

    @pytest.mark.skip()
    def test_get_columns(self, name):
        return

    @pytest.mark.skip()
    def test_get_pk_constraint(self, name):
        return

    @pytest.mark.skip()
    def test_get_foreign_keys(self, name):
        return

    @pytest.mark.skip()
    def test_get_indexes(self, name):
        return

    @pytest.mark.skip()
    def test_get_unique_constraints(self, name):
        return

    @pytest.mark.skip()
    def test_get_table_comment(self, name):
        return

    @pytest.mark.skip()
    def test_get_check_constraints(self, name):
        return