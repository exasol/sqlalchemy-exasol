# import all SQLAlchemy tests for this dialect
from inspect import cleandoc

import pytest
from sqlalchemy import (
    create_engine,
)
from sqlalchemy.schema import DDL
from sqlalchemy.sql import sqltypes
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
from sqlalchemy.testing.suite import ReturningGuardsTest as _ReturningGuardsTest
from sqlalchemy.testing.suite import RowCountTest as _RowCountTest
from sqlalchemy.testing.suite import RowFetchTest as _RowFetchTest
from sqlalchemy.testing.suite import TrueDivTest as _TrueDivTest

"""
Here, all tests are imported from the testing suite of sqlalchemy to ensure that the
Exasol dialect passes these expected tests. If a tests fails, it is investigated and,
if the underlying issue(s) cannot be resolved, overridden with a rationale & skip for
the test or that test condition (as some only fail for a specific DB driver).
"""
from sqlalchemy.testing.suite import *  # noqa: F403, F401
from sqlalchemy.testing.suite import testing
from sqlalchemy.testing.suite.test_ddl import (
    LongNameBlowoutTest as _LongNameBlowoutTest,
)

# Tests marked with xfail and this reason are failing after updating to SQLAlchemy 2.x.
# We will investigate and fix as many as possible in next PRs.
BREAKING_CHANGES_SQL_ALCHEMY_2x = (
    "Failing test after updating to SQLAlchemy 2.x. To be investigated."
)


class ReturningGuardsTest(_ReturningGuardsTest):
    @pytest.mark.xfail(reason=BREAKING_CHANGES_SQL_ALCHEMY_2x, strict=True)
    def test_delete_single(self):
        super().test_delete_single()

    @pytest.mark.xfail(reason=BREAKING_CHANGES_SQL_ALCHEMY_2x, strict=True)
    def test_insert_single(self):
        super().test_delete_single()

    @pytest.mark.xfail(reason=BREAKING_CHANGES_SQL_ALCHEMY_2x, strict=True)
    def test_update_single(self):
        super().test_update_single()


class TrueDivTest(_TrueDivTest):
    @pytest.mark.skipif(
        # only true atm for pyodbc -> need to investigate
        "pyodbc" in testing.db.dialect.driver,
        reason=BREAKING_CHANGES_SQL_ALCHEMY_2x,
    )
    @testing.combinations(("5.52", "2.4", "2.3"), argnames="left, right, expected")
    def test_truediv_numeric(self, connection, left, right, expected):
        super().test_truediv_numeric(connection, left, right, expected)


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
    @classmethod
    def define_views(cls, metadata):
        """Should be mostly identical to _HasTableTest, except where noted"""
        # column name "data" needs to be quoted as "data" is a reserved word
        query = 'CREATE VIEW vv AS SELECT id, "data" FROM test_table'

        event.listen(metadata, "after_create", DDL(query))
        event.listen(metadata, "before_drop", DDL("DROP VIEW vv"))

        if testing.requires.schemas.enabled:
            # column name "data" needs to be quoted as "data" is a reserved word
            query = (
                'CREATE VIEW {}.vv AS SELECT id, "data" FROM {}.test_table_s'.format(
                    config.test_schema,
                    config.test_schema,
                )
            )
            event.listen(metadata, "after_create", DDL(query))
            event.listen(
                metadata,
                "before_drop",
                DDL("DROP VIEW %s.vv" % (config.test_schema)),
            )

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

    @pytest.mark.xfail(reason=BREAKING_CHANGES_SQL_ALCHEMY_2x, strict=True)
    def test_has_table_cache(self, connection):
        super().test_has_table_cache(connection)


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

    @pytest.mark.xfail(reason=BREAKING_CHANGES_SQL_ALCHEMY_2x, strict=True)
    def test_non_rowcount_scenarios_no_raise(self):
        # says cursor already closed so very likely need to fix!
        super().test_non_rowcount_scenarios_no_raise()


class DifficultParametersTest(_DifficultParametersTest):
    tough_parameters = testing.combinations(
        ("boring",),
        ("per cent",),
        ("per % cent",),
        ("%percent",),
        ("par(ens)",),
        ("percent%(ens)yah",),
        ("col:ons",),
        ("_starts_with_underscore",),
        ("more :: %colons%",),
        ("_name",),
        ("___name",),
        ("[BracketsAndCase]",),
        ("42numbers",),
        ("percent%signs",),
        ("has spaces",),
        ("/slashes/",),
        ("more/slashes",),
        ("1param",),
        ("1col:on",),
        argnames="paramname",
    )

    @tough_parameters
    def test_round_trip_same_named_column(self, paramname, connection, metadata):
        # dot_s and qmarks are currently disabled see https://github.com/exasol/sqlalchemy-exasol/issues/232
        super().test_round_trip_same_named_column(paramname, connection, metadata)


# 700+ tests have errors now (many are combination tests); skip for now and handle later
@pytest.mark.xfail(reason=BREAKING_CHANGES_SQL_ALCHEMY_2x, strict=True)
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
    RATIONALE = (
        "This is likely a driver issue. We will investigate it in "
        "https://github.com/exasol/sqlalchemy-exasol/issues/539."
    )

    @pytest.mark.xfail("odbc" in testing.db.dialect.driver, reason=RATIONALE)
    @requirements.duplicate_key_raises_integrity_error
    def test_integrity_error(self):
        # Note: autocommit currently is needed to force error evaluation,
        #       otherwise errors will be swallowed.
        #       see also https://github.com/exasol/sqlalchemy-exasol/issues/120
        engine = create_engine(
            config.db.url,
            connect_args={"autocommit": True},
        )
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
        with config.db.begin() as conn:
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
    RATIONALE_PYODBC_DECIMAL = cleandoc(
        """FIXME: test skipped to allow upgrading to SQLAlchemy 1.3.x due
        to vulnerability in 1.2.x. Need to understand reason for this.
        Hypothesis is that the data type is not correctly coerced between
        EXASOL and pyodbc."""
    )

    @pytest.mark.skipif(
        "pyodbc" in testing.db.dialect.driver,
        reason=RATIONALE_PYODBC_DECIMAL,
    )
    @testing.requires.implicit_decimal_binds
    @testing.emits_warning(r".*does \*not\* support Decimal objects natively")
    def test_decimal_coerce_round_trip(self, connection):
        super().test_decimal_coerce_round_trip(connection)

    @pytest.mark.skipif(
        "pyodbc" in testing.db.dialect.driver,
        reason=BREAKING_CHANGES_SQL_ALCHEMY_2x + RATIONALE_PYODBC_DECIMAL,
    )
    @testing.requires.precision_numerics_general
    def test_precision_decimal(self, do_numeric_test):
        super().test_precision_decimal(do_numeric_test)

    @pytest.mark.skipif(
        "pyodbc" in testing.db.dialect.driver,
        reason=BREAKING_CHANGES_SQL_ALCHEMY_2x + RATIONALE_PYODBC_DECIMAL,
    )
    @testing.requires.precision_numerics_enotation_large
    def test_enotation_decimal(self, do_numeric_test):
        super().test_enotation_decimal(do_numeric_test)

    @pytest.mark.skipif(
        "pyodbc" in testing.db.dialect.driver,
        reason=BREAKING_CHANGES_SQL_ALCHEMY_2x + RATIONALE_PYODBC_DECIMAL,
    )
    @testing.requires.precision_numerics_enotation_large
    def test_enotation_decimal_large(self, do_numeric_test):
        super().test_enotation_decimal_large(do_numeric_test)

    @pytest.mark.skipif(
        "pyodbc" in testing.db.dialect.driver,
        reason=BREAKING_CHANGES_SQL_ALCHEMY_2x + RATIONALE_PYODBC_DECIMAL,
    )
    def test_numeric_as_decimal(self, do_numeric_test):
        super().test_numeric_as_decimal(do_numeric_test)

    @pytest.mark.skipif(
        "pyodbc" in testing.db.dialect.driver,
        reason=BREAKING_CHANGES_SQL_ALCHEMY_2x + RATIONALE_PYODBC_DECIMAL,
    )
    @testing.requires.fetch_null_from_numeric
    def test_numeric_null_as_decimal(self, do_numeric_test):
        super().test_numeric_null_as_decimal(do_numeric_test)

    @pytest.mark.xfail(reason=BREAKING_CHANGES_SQL_ALCHEMY_2x, strict=True)
    @testing.combinations(sqltypes.Float, sqltypes.Double, argnames="cls_")
    @testing.requires.float_is_numeric
    def test_float_is_not_numeric(self, connection, cls_):
        super().test_float_is_not_numeric()


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
