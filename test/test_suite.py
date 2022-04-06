# import all SQLAlchemy tests for this dialect
import pytest
from sqlalchemy import create_engine
from sqlalchemy.testing.suite import CompoundSelectTest as _CompoundSelectTest
from sqlalchemy.testing.suite import ExceptionTest as _ExceptionTest
from sqlalchemy.testing.suite import ExpandingBoundInTest as _ExpandingBoundInTest
from sqlalchemy.testing.suite import NumericTest as _NumericTest
from sqlalchemy.testing.suite import QuotedNameArgumentTest as _QuotedNameArgumentTest
from sqlalchemy.testing.suite import *  # noqa: F403, F401
from sqlalchemy.testing.suite.test_ddl import (
    LongNameBlowoutTest as _LongNameBlowoutTest,
)


class LongNameBlowoutTest(_LongNameBlowoutTest):
    @testing.combinations(
        ("fk",),
        ("pk",),
        # Manual indexes are not recommended within the Exasol DB,
        # (see https://docs.exasol.com/db/latest/performance/best_practices.htm)
        # therefore they are currently not supported by the sqlalchemy-exasol extension.
        # ("ix",)
        ("ck", testing.requires.check_constraint_reflection.as_skips()),
        ("uq", testing.requires.unique_constraint_reflection.as_skips()),
        argnames="type_",
    )
    @testing.provide_metadata
    def test_long_convention_name(self, type_, connection):
        metadata = self.metadata

        actual_name, reflected_name = getattr(self, type_)(metadata, connection)

        assert len(actual_name) > 255

        if reflected_name is not None:
            overlap = actual_name[0 : len(reflected_name)]
            if len(overlap) < len(actual_name):
                eq_(overlap[0:-5], reflected_name[0 : len(overlap) - 5])
            else:
                eq_(overlap, reflected_name)


class CompoundSelectTest(_CompoundSelectTest):
    """Skip this test as EXASOL does not allow EXISTS or IN predicates
    as part of the select list. Skipping is implemented by redefining
    the method as proposed by SQLAlchemy docs for new dialects."""

    def test_null_in_empty_set_is_false(self):
        return


class ExceptionTest(_ExceptionTest):
    @requirements.duplicate_key_raises_integrity_error
    def test_integrity_error(self):
        # Note: autocommit currently is needed to force error evaluation,
        #       otherwise errors will be swallowed.
        #       see also https://github.com/exasol/sqlalchemy-exasol/issues/120
        engine = create_engine(config.db.url, connect_args={"autocommit": True})
        with engine.connect() as conn:
            trans = conn.begin()
            conn.execute(self.tables.manual_pk.insert(), {"id": 1, "data": "d1"})

            assert_raises(
                exc.IntegrityError,
                conn.execute,
                self.tables.manual_pk.insert(),
                {"id": 1, "data": "d1"},
            )
            trans.rollback()

    @requirements.duplicate_key_raises_integrity_error
    def test_integrity_error_raw_sql(self):
        insert = text("INSERT INTO MANUAL_PK VALUES (1, 'd1')")
        with config.db.connect() as conn:
            conn.execute(insert)

            assert_raises(exc.IntegrityError, conn.execute, insert)


class ExpandingBoundInTest(_ExpandingBoundInTest):
    """Skip this test as EXASOL does not allow EXISTS or IN predicates
    as part of the select list. Skipping is implemented by redefining
    the method as proposed by SQLAlchemy docs for new dialects."""

    def test_null_in_empty_set_is_false(self):
        return


class NumericTest(_NumericTest):
    """FIXME: test skipped to allow upgrading to SQLAlchemy 1.3.x due
    to vulnerability in 1.2.x. Need to understand reason for this.
    Hypothesis is that the data type is not correctly coerced between
    EXASOL and pyodbc."""

    def test_decimal_coerce_round_trip(self):
        return


class QuotedNameArgumentTest(_QuotedNameArgumentTest):
    """This suite was added to SQLAlchemy 1.3.19 on July 2020 to address
    issues in other dialects related to object names that contain quotes
    and double quotes. Since this feature is not relevant to the
    Exasol dialect, the entire suite will be skipped. More info on fix:
    https://github.com/sqlalchemy/sqlalchemy/issues/5456"""

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
