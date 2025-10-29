from sqlalchemy.testing import exclusions
from sqlalchemy.testing.exclusions import (
    BooleanPredicate,
    skip_if,
)
from sqlalchemy.testing.requirements import SuiteRequirements


class Requirements(SuiteRequirements):
    @property
    def reflects_pk_names(self):
        return exclusions.open()

    @property
    def index_reflection(self):
        return exclusions.closed()

    @property
    def unique_constraint_reflection(self):
        """target dialect supports reflection of unique constraints"""
        return exclusions.closed()

    @property
    def self_referential_foreign_keys(self):
        """Target database must support self-referential foreign keys."""
        return exclusions.open()

    @property
    def implicitly_named_constraints(self):
        """target database must apply names to unnamed constraints."""
        return exclusions.open()

    @property
    def returning(self):
        """target platform supports RETURNING."""
        return exclusions.closed()

    @property
    def empty_strings_varchar(self):
        """target database can persist/return an empty string with a
        varchar."""
        return exclusions.closed()

    @property
    def text_type(self):
        """Target database must support an unbounded Text()
        type such as TEXT or CLOB"""
        return exclusions.closed()

    @property
    def datetime_microseconds(self):
        """target dialect supports representation of Python
        datetime.datetime() with microsecond objects."""
        return exclusions.closed()

    @property
    def datetime_historic(self):
        """target dialect supports representation of Python
        datetime.datetime() objects with historic (pre 1970) values."""
        return exclusions.open()

    @property
    def date_historic(self):
        """target dialect supports representation of Python
        datetime.date() objects with historic (pre 1970) values."""
        return exclusions.open()

    @property
    def time(self):
        """target dialect supports representation of Python
        datetime.time() objects."""
        return exclusions.closed()

    @property
    def time_microseconds(self):
        """target dialect supports representation of Python
        datetime.time() with microsecond objects."""
        return exclusions.closed()

    @property
    def unbounded_varchar(self):
        """Target database must support VARCHAR with no length"""
        return exclusions.closed()

    @property
    def implements_get_lastrowid(self):
        """ "target dialect implements the executioncontext.get_lastrowid()
        method without reliance on RETURNING."""
        return exclusions.closed()

    @property
    def emulated_lastrowid(self):
        """ "target dialect retrieves cursor.lastrowid, or fetches
        from a database-side function after an insert() construct executes,
        within the get_lastrowid() method.

        Only dialects that "pre-execute", or need RETURNING to get last
        inserted id, would return closed/fail/skip for this.
        """
        return exclusions.open()

    @property
    def schemas(self):
        """Target database supports named schemas"""
        return exclusions.open()

    @property
    def views(self):
        """Target database must support VIEWs."""

        return exclusions.open()

    @property
    def view_reflection(self):
        """Target database supports view metadata"""
        return exclusions.open()

    @property
    def precision_numerics_enotation_large(self):
        """Dialect converts small/large scale decimals into scientific notation"""
        return exclusions.open()

    @property
    def temporary_tables(self):
        """target database supports temporary tables"""
        return exclusions.closed()

    @property
    def temp_table_names(self):
        """target dialect supports listing of temporary table names"""
        return exclusions.closed()

    @property
    def temp_table_reflection(self):
        return exclusions.closed()

    @property
    def offset(self):
        """target database can render OFFSET, or an equivalent, in a
        SELECT.
        """
        return exclusions.closed()

    @property
    def order_by_col_from_union(self):
        """target database supports ordering by a column from a SELECT
        inside of a UNION
        E.g.  (SELECT id, ...) UNION (SELECT id, ...) ORDER BY id"""
        return exclusions.open()

    @property
    def bound_limit_offset(self):
        """target database can render LIMIT and/or OFFSET using a bound
        parameter
        """
        return exclusions.closed()

    @property
    def duplicate_key_raises_integrity_error(self):
        return exclusions.only_on(
            [lambda config: config.db.dialect.driver == "pyodbc"],
            reason="Currently this is only supported by pyodbc based dialects",
        )

    @property
    def independent_connections(self):
        return exclusions.open()

    @property
    def parens_in_union_contained_select_w_limit_offset(self):
        return exclusions.closed()

    @property
    def parens_in_union_contained_select_wo_limit_offset(self):
        return exclusions.closed()

    @property
    def broken_cx_oracle6_numerics(config):
        return exclusions.closed()

    @property
    def cross_schema_fk_reflection(self):
        return exclusions.closed()

    @property
    def ctes(self):
        """Target database supports CTEs"""
        return skip_if(
            BooleanPredicate(
                True,
                "Can't be opened as CTE tests require DB support for 'WITH RECURSIVE' not supported by EXASOL",
            )
        )

    @property
    def standalone_null_binds_whereclause(self):
        """target database/driver supports bound parameters with NULL in the
        WHERE clause, in situations where it has to be typed.
        """
        return exclusions.closed()

    @property
    def binary_literals(self):
        """target backend supports simple binary literals, e.g. an
        expression like::

            SELECT CAST('foo' AS BINARY)

        Where ``BINARY`` is the type emitted from :class:`.LargeBinary`,
        e.g. it could be ``BLOB`` or similar.

        Basically fails on Oracle.

        """
        return skip_if(
            BooleanPredicate(
                True, """A binary type is not natively supported by the EXASOL DB"""
            )
        )

    @property
    def binary_comparisons(self):
        """target database/driver can allow BLOB/BINARY fields to be compared
        against a bound parameter value.
        """
        return skip_if(
            BooleanPredicate(
                True, """A binary type is not natively supported by the EXASOL DB"""
            )
        )

    @property
    def sql_expression_limit_offset(self):
        """
        This feature roughly expects the following query types to be available:

        - SELECT * FROM <table> ORDER BY <col> ASC LIMIT <expr>;
        - SELECT * FROM <table> ORDER BY <col> ASC LIMIT <expr> OFFSET <expr>;
        - SELECT * FROM <table> ORDER BY <col> ASC LIMIT <expr> OFFSET <literal/value>;
        - SELECT * FROM <table> ORDER BY <col> ASC OFFSET <expr>;
              Exasol -> SELECT * FROM <table> ORDER BY <col> ASC LIMIT <offset>, <count>;
        - SELECT * FROM <table> ORDER BY <col> ASC LIMIT <count> OFFSET <expr>;
        """
        return skip_if(BooleanPredicate(True, """Not Implemented Yet"""))
