# import all SQLAlchemy tests for this dialect
from enum import Enum
from inspect import cleandoc

import pytest
import sqlalchemy as sa
from pyexasol import ExaQueryError
from sqlalchemy.schema import (
    DDL,
    Index,
)
from sqlalchemy.sql import sqltypes
from sqlalchemy.testing.suite import ComponentReflectionTest as _ComponentReflectionTest
from sqlalchemy.testing.suite import CompoundSelectTest as _CompoundSelectTest
from sqlalchemy.testing.suite import DifficultParametersTest as _DifficultParametersTest
from sqlalchemy.testing.suite import ExceptionTest as _ExceptionTest
from sqlalchemy.testing.suite import HasIndexTest as _HasIndexTest
from sqlalchemy.testing.suite import HasTableTest as _HasTableTest
from sqlalchemy.testing.suite import InsertBehaviorTest as _InsertBehaviorTest
from sqlalchemy.testing.suite import LongNameBlowoutTest as _LongNameBlowoutTest
from sqlalchemy.testing.suite import NumericTest as _NumericTest
from sqlalchemy.testing.suite import QuotedNameArgumentTest as _QuotedNameArgumentTest
from sqlalchemy.testing.suite import ReturningGuardsTest as _ReturningGuardsTest
from sqlalchemy.testing.suite import RowCountTest as _RowCountTest
from sqlalchemy.testing.suite import RowFetchTest as _RowFetchTest

"""
Here, all tests are imported from the testing suite of sqlalchemy to ensure that the
Exasol dialect passes these expected tests. If a tests fails, it is investigated and,
if the underlying issue(s) cannot be resolved, override them with a rationale & xfail for
the test or that test condition.
"""
from sqlalchemy.testing.suite import *  # noqa: F403, F401
from sqlalchemy.testing.suite import testing

# Tests marked with xfail and this reason are failing after updating to SQLAlchemy 2.x.
# We will investigate and fix as many as possible in next PRs.
BREAKING_CHANGES_SQL_ALCHEMY_2x = (
    "Failing test after updating to SQLAlchemy 2.x. To be investigated."
)


class XfailRationale(str, Enum):
    MANUAL_INDEX = cleandoc(
        """sqlalchemy-exasol does not support manual indexes.
        (see https://docs.exasol.com/db/latest/performance/indexes.htm#Manualindexoperations)
        Manual indexes are not recommended within the Exasol DB.
        """
    )
    NEW_FEATURE_2x = cleandoc(
        """In migrating to 2.x, new features were introduced by SQLAlchemy that
        have not yet been implemented in sqlalchemy-exasol."""
    )
    QUOTING = cleandoc(
        """This suite was added to SQLAlchemy 1.3.19 on July 2020 to address
        issues in other dialects related to object names that contain quotes
        and double quotes. Since this feature is not relevant to the
        Exasol dialect, the entire suite is set to xfail. For further info, see:
        https://github.com/sqlalchemy/sqlalchemy/issues/5456"""
    )
    SELECT_LIST = cleandoc(
        """Exasol does not allow EXISTS or IN predicates as part of the select list."""
    )


class ReturningGuardsTest(_ReturningGuardsTest):
    """
    Exasol does not support the RETURNING clause. This is already the assumption
    per the DefaultDialect.

    The single tests of class sqlalchemy.testing.suite.ReturningGuardsTest are
    overridden, as they are written to send the request to the DB and receive an
    error from the DB itself. For the websocket driver (based on PyExasol), the
    exception raised is an ExaQueryError and not a DBAPIError.
    """

    @staticmethod
    def _run_test(test_method, connection, run_stmt):
        with pytest.raises(ExaQueryError):
            test_method(connection, run_stmt)

    def test_delete_single(self, connection, run_stmt):
        self._run_test(super().test_delete_single, connection, run_stmt)

    def test_insert_single(self, connection, run_stmt):
        self._run_test(super().test_insert_single, connection, run_stmt)

    def test_update_single(self, connection, run_stmt):
        self._run_test(super().test_update_single, connection, run_stmt)


class RowFetchTest(_RowFetchTest):
    RATIONAL = cleandoc(
        """
    PyExasol currently does not support/allow duplicate names in the results set.

    See also:
    * pyexasol.statement.ExaStatement._check_duplicate_col_names
    """
    )

    @testing.config.requirements.duplicate_names_in_cursor_description
    @pytest.mark.xfail(reason=RATIONAL, strict=True)
    def test_row_with_dupe_names(self, connection):
        super().test_row_with_dupe_names(connection)


class HasTableTest(_HasTableTest):
    @classmethod
    def define_views(cls, metadata):
        """
        Default implementation of define_views in
        class sqlalchemy.testing.suite.HasTableTest
        needs to be overridden here as Exasol treats "data" as a reserved word &
        requires quoting. Changes to the original implementation are marked with
        'Note:'.
        """
        # Note: column name "data" needs to be quoted as "data" is a reserved word
        query = 'CREATE VIEW vv AS SELECT id, "data" FROM test_table'

        event.listen(metadata, "after_create", DDL(query))
        event.listen(metadata, "before_drop", DDL("DROP VIEW vv"))

        if testing.requires.schemas.enabled:
            # Note: column name "data" needs to be quoted as "data" is a reserved word
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

    @pytest.mark.xfail(reason=BREAKING_CHANGES_SQL_ALCHEMY_2x, strict=True)
    def test_has_table_cache(self, connection):
        super().test_has_table_cache(connection)


class InsertBehaviorTest(_InsertBehaviorTest):
    @pytest.mark.xfail(
        reason="This currently isn't supported by the websocket protocol L3-1064.",
        strict=True,
    )
    @testing.requires.empty_inserts_executemany
    def test_empty_insert_multiple(self, connection):
        super().test_empty_insert_multiple(connection)


class RowCountTest(_RowCountTest):
    @pytest.mark.xfail(reason=BREAKING_CHANGES_SQL_ALCHEMY_2x, strict=True)
    def test_non_rowcount_scenarios_no_raise(self):
        # says cursor already closed so very likely need to fix!
        super().test_non_rowcount_scenarios_no_raise()


class ComponentReflectionTest(_ComponentReflectionTest):
    @classmethod
    def define_reflected_tables(cls, metadata, schema):
        """
        Default implementation of define_reflected_tables in
        class sqlalchemy.testing.suite.ComponentReflectionTest
        needs to be overridden here as Exasol does not support column constraints
        and manages indexes on its own. The code given in this overriding class
        method was directly copied. See notes, marked with 'Commented out', highlighting
        the changed places.
        """
        if schema:
            schema_prefix = schema + "."
        else:
            schema_prefix = ""

        if testing.requires.self_referential_foreign_keys.enabled:
            parent_id_args = (
                ForeignKey("%susers.user_id" % schema_prefix, name="user_id_fk"),
            )
        else:
            parent_id_args = ()
        users = Table(
            "users",
            metadata,
            Column("user_id", sa.INT, primary_key=True),
            Column("test1", sa.CHAR(5), nullable=False),
            Column("test2", sa.Float(), nullable=False),
            Column("parent_user_id", sa.Integer, *parent_id_args),
            # Commented out, as Exasol does not support column constraints
            # sa.CheckConstraint(
            #     "test2 > 0",
            #     name="zz_test2_gt_zero",
            #     comment="users check constraint",
            # ),
            # sa.CheckConstraint("test2 <= 1000"),
            schema=schema,
            test_needs_fk=True,
        )

        Table(
            "dingalings",
            metadata,
            Column("dingaling_id", sa.Integer, primary_key=True),
            Column(
                "address_id",
                sa.Integer,
                ForeignKey(
                    "%semail_addresses.address_id" % schema_prefix,
                    name="zz_email_add_id_fg",
                    comment="di fk comment",
                ),
            ),
            Column(
                "id_user",
                sa.Integer,
                ForeignKey("%susers.user_id" % schema_prefix),
            ),
            # Commented out, as Exasol does not support unique constraints beyond primary keys
            Column("data", sa.String(30)),  # , unique=True),
            # Commented out, as Exasol does not support column constraints
            # sa.CheckConstraint(
            #     "address_id > 0 AND address_id < 1000",
            #     name="address_id_gt_zero",
            # ),
            # sa.UniqueConstraint(
            #     "address_id",
            #     "dingaling_id",
            #     name="zz_dingalings_multiple",
            #     comment="di unique comment",
            # ),
            schema=schema,
            test_needs_fk=True,
        )
        Table(
            "email_addresses",
            metadata,
            Column("address_id", sa.Integer),
            Column("remote_user_id", sa.Integer, ForeignKey(users.c.user_id)),
            # Commented out, as Exasol manages indices internally
            Column("email_address", sa.String(20)),  # , index=True),
            sa.PrimaryKeyConstraint(
                "address_id", name="email_ad_pk", comment="ea pk comment"
            ),
            schema=schema,
            test_needs_fk=True,
        )
        Table(
            "comment_test",
            metadata,
            Column("id", sa.Integer, primary_key=True, comment="id comment"),
            Column("data", sa.String(20), comment="data % comment"),
            Column(
                "d2",
                sa.String(20),
                comment=r"""Comment types type speedily ' " \ '' Fun!""",
            ),
            Column("d3", sa.String(42), comment="Comment\nwith\rescapes"),
            schema=schema,
            comment=r"""the test % ' " \ table comment""",
        )
        Table(
            "no_constraints",
            metadata,
            Column("data", sa.String(20)),
            schema=schema,
            comment="no\nconstraints\rhas\fescaped\vcomment",
        )

        if testing.requires.cross_schema_fk_reflection.enabled:
            if schema is None:
                Table(
                    "local_table",
                    metadata,
                    Column("id", sa.Integer, primary_key=True),
                    Column("data", sa.String(20)),
                    Column(
                        "remote_id",
                        ForeignKey("%s.remote_table_2.id" % testing.config.test_schema),
                    ),
                    test_needs_fk=True,
                    schema=config.db.dialect.default_schema_name,
                )
            else:
                Table(
                    "remote_table",
                    metadata,
                    Column("id", sa.Integer, primary_key=True),
                    Column(
                        "local_id",
                        ForeignKey(
                            "%s.local_table.id" % config.db.dialect.default_schema_name
                        ),
                    ),
                    Column("data", sa.String(20)),
                    schema=schema,
                    test_needs_fk=True,
                )
                Table(
                    "remote_table_2",
                    metadata,
                    Column("id", sa.Integer, primary_key=True),
                    Column("data", sa.String(20)),
                    schema=schema,
                    test_needs_fk=True,
                )

        if testing.requires.index_reflection.enabled:
            Index("users_t_idx", users.c.test1, users.c.test2, unique=True)
            Index("users_all_idx", users.c.user_id, users.c.test2, users.c.test1)

            if not schema:
                # test_needs_fk is at the moment to force MySQL InnoDB
                noncol_idx_test_nopk = Table(
                    "noncol_idx_test_nopk",
                    metadata,
                    Column("q", sa.String(5)),
                    test_needs_fk=True,
                )

                noncol_idx_test_pk = Table(
                    "noncol_idx_test_pk",
                    metadata,
                    Column("id", sa.Integer, primary_key=True),
                    Column("q", sa.String(5)),
                    test_needs_fk=True,
                )

                if (
                    testing.requires.indexes_with_ascdesc.enabled
                    and testing.requires.reflect_indexes_with_ascdesc.enabled
                ):
                    Index("noncol_idx_nopk", noncol_idx_test_nopk.c.q.desc())
                    Index("noncol_idx_pk", noncol_idx_test_pk.c.q.desc())

        if testing.requires.view_column_reflection.enabled:
            cls.define_views(metadata, schema)
        if not schema and testing.requires.temp_table_reflection.enabled:
            cls.define_temp_tables(metadata)

    @pytest.mark.xfail(reason=XfailRationale.MANUAL_INDEX.value)
    def test_get_indexes(self, connection, use_schema):
        super().test_get_indexes()

    @pytest.mark.xfail(reason=XfailRationale.NEW_FEATURE_2x.value, strict=True)
    def test_get_multi_columns(self):
        # See https://docs.sqlalchemy.org/en/20/core/reflection.html#sqlalchemy.engine.reflection.Inspector.get_multi_columns
        super().test_get_multi_columns()

    @pytest.mark.xfail(reason=XfailRationale.NEW_FEATURE_2x.value, strict=True)
    def test_get_multi_foreign_keys(self):
        # See https://docs.sqlalchemy.org/en/20/core/reflection.html#sqlalchemy.engine.reflection.Inspector.get_multi_foreign_keys
        super().test_get_multi_foreign_keys()


class HasIndexTest(_HasIndexTest):
    @pytest.mark.xfail(reason=XfailRationale.MANUAL_INDEX.value, strict=True)
    def test_has_index(self):
        super().test_has_index()

    @pytest.mark.xfail(reason=XfailRationale.MANUAL_INDEX.value, strict=True)
    @testing.requires.schemas
    def test_has_index_schema(self):
        super().test_has_index_schema()


class LongNameBlowoutTest(_LongNameBlowoutTest):
    testing_parameters = testing.combinations(
        ("fk",),
        ("pk",),
        ("ix",),
        ("ck", testing.requires.check_constraint_reflection.as_skips()),
        ("uq", testing.requires.unique_constraint_reflection.as_skips()),
        argnames="type_",
    )

    @testing_parameters
    def test_long_convention_name(self, type_, metadata, connection):
        """
        The default implementation of test_long_convention_name in
        class sqlalchemy.testing.suite.LongNameBlowoutTest needs to be
        overridden here as Exasol does not support manually created indices.
        Beyond the first check, if `type_ == "ix"`, the rest of the code
        has been copied without modification.
        """

        if type_ == "ix":
            pytest.xfail(reason=XfailRationale.MANUAL_INDEX.value)

        actual_name, reflected_name = getattr(self, type_)(metadata, connection)

        assert len(actual_name) > 255

        if reflected_name is not None:
            overlap = actual_name[0 : len(reflected_name)]
            if len(overlap) < len(actual_name):
                eq_(overlap[0:-5], reflected_name[0 : len(overlap) - 5])
            else:
                eq_(overlap, reflected_name)


class CompoundSelectTest(_CompoundSelectTest):
    @pytest.mark.xfail(reason=XfailRationale.SELECT_LIST.value, strict=True)
    def test_null_in_empty_set_is_false(self, connection):
        self.test_null_in_empty_set_is_false(connection)


class ExceptionTest(_ExceptionTest):
    RATIONALE = """
    The websocket-based dialect does not yet support raising an
    error on a duplicate key. This was noted before as an issue
    for the deprecated ODBC-based dialects in:
      - https://github.com/exasol/sqlalchemy-exasol/issues/539
      - https://github.com/exasol/sqlalchemy-exasol/issues/120
    """

    @pytest.mark.xfail(reason=RATIONALE, strict=True)
    @requirements.duplicate_key_raises_integrity_error
    def test_integrity_error(self):
        super().test_integrity_error()

    @pytest.mark.xfail(reason=RATIONALE, strict=True)
    @requirements.duplicate_key_raises_integrity_error
    def test_integrity_error_raw_sql(self):
        """
        Additional test that is related that our developers added.
        """
        insert = text("INSERT INTO MANUAL_PK VALUES (1, 'd1')")
        with config.db.begin() as conn:
            conn.execute(insert)
            assert_raises(exc.IntegrityError, conn.execute, insert)


@pytest.mark.xfail(reason=XfailRationale.QUOTING.value, strict=True)
class QuotedNameArgumentTest(_QuotedNameArgumentTest):
    pass


class NumericTest(_NumericTest):
    RATIONALE = """
    The Exasol target backend maps Numeric to Decimal. Decimal is also used for both
    Float & Double. Thus, we expect this test to fail.
    """

    @pytest.mark.xfail(reason=RATIONALE, strict=True)
    @testing.combinations(sqltypes.Float, sqltypes.Double, argnames="cls_")
    @testing.requires.float_is_numeric
    def test_float_is_not_numeric(self, connection, cls_):
        super().test_float_is_not_numeric()


class DifficultParametersTest(_DifficultParametersTest):
    @_DifficultParametersTest.tough_parameters
    @config.requirements.unusual_column_name_characters
    def test_round_trip_same_named_column(self, paramname, connection, metadata):
        if testing.db.dialect.server_version_info <= (7, 1, 30):
            # This does not work for Exasol DB versions <= 7.1.30.
            # See: https://github.com/exasol/sqlalchemy-exasol/issues/232
            if paramname == "dot.s":
                pytest.xfail(reason="dot.s does not work for <= 7.1.30")
        super().test_round_trip_same_named_column(paramname, connection, metadata)
