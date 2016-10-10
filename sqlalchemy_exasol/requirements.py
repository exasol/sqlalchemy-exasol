from sqlalchemy.testing.requirements import SuiteRequirements

from sqlalchemy.testing import exclusions

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
    def returning(self):
        """target platform supports RETURNING."""
        return exclusions.closed()
    
    @property
    def empty_strings_varchar(self):
        """target database can persist/return an empty string with a
        varchar. """
        return exclusions.closed()

    @property
    def text_type(self):
        """Target database must support an unbounded Text() 
        type such as TEXT or CLOB """
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
        """"target dialect implements the executioncontext.get_lastrowid()
            method without reliance on RETURNING."""
        return exclusions.closed()

    @property
    def emulated_lastrowid(self):
        """"target dialect retrieves cursor.lastrowid, or fetches
        from a database-side function after an insert() construct executes,
        within the get_lastrowid() method.
    
        Only dialects that "pre-execute", or need RETURNING to get last
        inserted id, would return closed/fail/skip for this.
        """
        return exclusions.open()

    @property
    def schemas(self):
        """Target database supports named schemas
        """
        return exclusions.open()

    @property
    def views(self):
        """Target database must support VIEWs."""

        return exclusions.open()

    @property
    def view_reflection(self):
        """Target database supports view metadata
        """
        return exclusions.open()

    @property
    def precision_numerics_enotation_large(self):
        """Dialect converts small/large scale decimals into scientific notation
        """
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
    def bound_limit_offset(self):
        """target database can render LIMIT and/or OFFSET using a bound
        parameter
        """

        return exclusions.closed()

    @property
    def duplicate_key_raises_integrity_error(self):
        return exclusions.closed()

    @property
    def independent_connections(self):
        return exclusions.open()

    @property
    def parens_in_union_contained_select_w_limit_offset(self):
        return exclusions.closed()

    @property
    def parens_in_union_contained_select_wo_limit_offset(self):
        return exclusions.closed()
