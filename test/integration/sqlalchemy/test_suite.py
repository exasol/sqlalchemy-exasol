# import all SQLAlchemy tests for this dialect
from inspect import cleandoc

import pytest
from sqlalchemy import (
    create_engine,
    testing,
)
from sqlalchemy.testing.suite import ComponentReflectionTest as _ComponentReflectionTest
from sqlalchemy.testing.suite import CompoundSelectTest as _CompoundSelectTest
from sqlalchemy.testing.suite import DifficultParametersTest as _DifficultParametersTest
from sqlalchemy.testing.suite import ExceptionTest as _ExceptionTest
from sqlalchemy.testing.suite import ExpandingBoundInTest as _ExpandingBoundInTest
from sqlalchemy.testing.suite import HasIndexTest as _HasIndexTest
from sqlalchemy.testing.suite import HasTableTest as _HasTableTest
from sqlalchemy.testing.suite import InsertBehaviorTest as _InsertBehaviorTest
from sqlalchemy.testing.suite import NumericTest as _NumericTest
from sqlalchemy.testing.suite import QuotedNameArgumentTest as _QuotedNameArgumentTest
from sqlalchemy.testing.suite import RowCountTest as _RowCountTest
from sqlalchemy.testing.suite import RowFetchTest as _RowFetchTest
from sqlalchemy.testing.suite import *  # noqa: F403, F401
from sqlalchemy.testing.suite.test_ddl import (
    LongNameBlowoutTest as _LongNameBlowoutTest,
)


class RowFetchTest(_RowFetchTest):
    RATIONAL = cleandoc(
        """
    PyExasol currently does not support/allow duplicate names in the results set.
    
    See also: 
    * pyexasol.statement.ExaStatement._check_duplicate_col_names
    """
    )

    @testing.config.requirements.duplicate_names_in_cursor_description
    @pytest.mark.skipif("websocket" in testing.db.dialect.driver, reason=RATIONAL)
    def test_row_with_dupe_names(self, connection):
        super().test_row_with_dupe_names(connection)


class HasTableTest(_HasTableTest):
    RATIONALE = cleandoc(
        """
    The Exasol dialect does not check against views for `has_table`, see also `Inspector.has_table()`.
    
    This behaviour is subject to change with sqlalchemy 2.0.
    See also:
    * https://github.com/sqlalchemy/sqlalchemy/blob/3fc6c40ea77c971d3067dab0fdf57a5b5313b69b/lib/sqlalchemy/engine/reflection.py#L415
    * https://github.com/sqlalchemy/sqlalchemy/discussions/8678
    * https://github.com/sqlalchemy/sqlalchemy/commit/f710836488162518dcf2dc1006d90ecd77a2a178
    """
    )

    @pytest.mark.xfail(reason=RATIONALE, strict=True)
    @testing.requires.views
    def test_has_table_view(self, connection):
        super().test_has_table_view(connection)

    @pytest.mark.xfail(reason=RATIONALE, strict=True)
    @testing.requires.views
    @testing.requires.schemas
    def test_has_table_view_schema(self, connection):
        super().test_has_table_view_schema(connection)


class InsertBehaviorTest(_InsertBehaviorTest):
    @pytest.mark.xfail(
        "turbodbc" in testing.db.dialect.driver,
        reason=cleandoc(
            """
        This test is failing for turbodbc and haven't been investigated yet.
        Attention:
        * turbodbc maintenance is paused until if it is clear if there is still demand for it
        """
        ),
        strict=True,
    )
    @pytest.mark.xfail(
        "websocket" in testing.db.dialect.driver,
        reason="This currently isn't supported by the websocket protocol L3-1064.",
        strict=True,
    )
    @testing.requires.empty_inserts_executemany
    def test_empty_insert_multiple(self, connection):
        super().test_empty_insert_multiple(connection)


class RowCountTest(_RowCountTest):
    PYODBC_RATIONALE = cleandoc(
        """
        pyodbc does not support returning the actual affected rows when executemany is used,
        the cursor result always will be set to the rowcount = -1 in this case.
        This also is a valid behaviour according to the python DBAPI specification.
        For more details see also:
        * https://peps.python.org/pep-0249/ 
        * https://peps.python.org/pep-0249/#rowcount
        * https://peps.python.org/pep-0249/#id21
        * https://peps.python.org/pep-0249/#executemany
        """
    )

    TURBODBC_RATIONALE = cleandoc(
        """
        The currently used turbodbc driver returns invalid results.
        Attention: 
        * turbodbc maintenance is paused until if it is clear if there is still demand for it
        * If this tests will succeed in the future consider repining the turbodbc driver
          dependency in order to provide support for this "features".
        """
    )

    @pytest.mark.xfail(
        "turbodbc" in testing.db.dialect.driver, reason=TURBODBC_RATIONALE, strict=True
    )
    @pytest.mark.skipif("pyodbc" in testing.db.dialect.driver, reason=PYODBC_RATIONALE)
    @testing.requires.sane_multi_rowcount
    def test_multi_update_rowcount(self, connection):
        super().test_multi_update_rowcount(connection)

    @pytest.mark.xfail(
        "turbodbc" in testing.db.dialect.driver, reason=TURBODBC_RATIONALE, strict=True
    )
    @pytest.mark.skipif("pyodbc" in testing.db.dialect.driver, reason=PYODBC_RATIONALE)
    @testing.requires.sane_multi_rowcount
    def test_multi_delete_rowcount(self, connection):
        super().test_multi_delete_rowcount(connection)

    @pytest.mark.xfail(
        "turbodbc" in testing.db.dialect.driver, reason=TURBODBC_RATIONALE, strict=True
    )
    def test_update_rowcount1(self, connection):
        super().test_update_rowcount1(connection)

    @pytest.mark.xfail(
        "turbodbc" in testing.db.dialect.driver, reason=TURBODBC_RATIONALE, strict=True
    )
    def test_update_rowcount2(self, connection):
        super().test_update_rowcount2(connection)

    @pytest.mark.xfail(
        "turbodbc" in testing.db.dialect.driver, reason=TURBODBC_RATIONALE, strict=True
    )
    def test_delete_rowcount(self, connection):
        super().test_delete_rowcount(connection)

    @pytest.mark.xfail(
        "turbodbc" in testing.db.dialect.driver, reason=TURBODBC_RATIONALE, strict=True
    )
    @testing.requires.sane_rowcount_w_returning
    def test_update_rowcount_return_defaults(self, connection):
        super().test_update_rowcount_return_defaults(connection)


class DifficultParametersTest(_DifficultParametersTest):
    @pytest.mark.xfail(reason="https://github.com/exasol/sqlalchemy-exasol/issues/232")
    @testing.combinations(
        ("boring",),
        ("per cent",),
        ("per % cent",),
        ("%percent",),
        ("par(ens)",),
        ("percent%(ens)yah",),
        ("col:ons",),
        ("more :: %colons%",),
        ("/slashes/",),
        ("more/slashes",),
        ("q?marks",),
        ("1param",),
        ("1col:on",),
        argnames="name",
    )
    def test_round_trip(self, name, connection, metadata):
        super().test_round_trip(name, connection, metadata)


class ComponentReflectionTest(_ComponentReflectionTest):
    @pytest.mark.skip(reason="EXASOL has no explicit indexes")
    def test_get_indexes(self, connection, use_schema):
        super().test_get_indexes()


class HasIndexTest(_HasIndexTest):
    RATIONAL = """EXASOL does not support no explicit indexes"""

    @pytest.mark.skip(reason=RATIONAL)
    def test_has_index(self):
        super().test_has_index()

    @pytest.mark.skip(reason=RATIONAL)
    @testing.requires.schemas
    def test_has_index_schema(self):
        super().test_has_index_schema()


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
    @pytest.mark.skip(
        reason=cleandoc(
            """Skip this test as EXASOL does not allow EXISTS or IN predicates
        as part of the select list. Skipping is implemented by redefining
        the method as proposed by SQLAlchemy docs for new dialects."""
        )
    )
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
    @pytest.mark.skip(
        reason=cleandoc(
            """Skip this test as EXASOL does not allow EXISTS or IN predicates
        as part of the select list. Skipping is implemented by redefining
        the method as proposed by SQLAlchemy docs for new dialects."""
        )
    )
    def test_null_in_empty_set_is_false(self):
        return


class NumericTest(_NumericTest):
    @pytest.mark.skipif(
        "pyodbc" in testing.db.dialect.driver,
        reason=cleandoc(
            """FIXME: test skipped to allow upgrading to SQLAlchemy 1.3.x due
        to vulnerability in 1.2.x. Need to understand reason for this.
        Hypothesis is that the data type is not correctly coerced between
        EXASOL and pyodbc."""
        ),
    )
    @testing.requires.implicit_decimal_binds
    @testing.emits_warning(r".*does \*not\* support Decimal objects natively")
    def test_decimal_coerce_round_trip(self, connection):
        super().test_decimal_coerce_round_trip(connection)


class QuotedNameArgumentTest(_QuotedNameArgumentTest):
    RATIONAL = cleandoc(
        """This suite was added to SQLAlchemy 1.3.19 on July 2020 to address
        issues in other dialects related to object names that contain quotes
        and double quotes. Since this feature is not relevant to the
        Exasol dialect, the entire suite will be skipped. More info on fix:
        https://github.com/sqlalchemy/sqlalchemy/issues/5456"""
    )

    @pytest.mark.skip(reason=RATIONAL)
    def test_get_table_options(self, name):
        return

    @pytest.mark.skip(reason=RATIONAL)
    def test_get_view_definition(self, name):
        return

    @pytest.mark.skip(reason=RATIONAL)
    def test_get_columns(self, name):
        return

    @pytest.mark.skip(reason=RATIONAL)
    def test_get_pk_constraint(self, name):
        return

    @pytest.mark.skip(reason=RATIONAL)
    def test_get_foreign_keys(self, name):
        return

    @pytest.mark.skip(reason=RATIONAL)
    def test_get_indexes(self, name):
        return

    @pytest.mark.skip(reason=RATIONAL)
    def test_get_unique_constraints(self, name):
        return

    @pytest.mark.skip(reason=RATIONAL)
    def test_get_table_comment(self, name):
        return

    @pytest.mark.skip(reason=RATIONAL)
    def test_get_check_constraints(self, name):
        return
