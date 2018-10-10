# -*- coding: utf-8 -*-
"""Support for the EXASOL database.

Auto Increment Behavior
-----------------------

``IDENTITY`` columns are supported by using SQLAlchemy
``schema.Sequence()`` objects. Example:

    from sqlalchemy import Table, Integer, String, Sequence, Column

    Table('test', metadata,
           Column('id', Integer,
                  Sequence('blah',1000), primary_key=True),
           Column('name', String(20))
         ).create(some_engine)

will yield::

   CREATE TABLE test (
     id INTEGER IDENTITY 1000,
     name VARCHAR(20) NULL,
     PRIMARY KEY(id)
     )

Note that the ``start`` value for sequences is optional and will default to 1.
The start value of a sequence cannot be retrieved when reflecting a Table
object.
The autoincrement flag for Column Objects is not supporte by exadialect.

Identifier Casing
-----------------

EXASol mimics the behavior of Oracle. Thus, for this dialect implementation
the Oracle dialect was taken as a reference.
In EXASol, the data dictionary represents all case insensitive identifier names
using UPPERCASE text.SQLAlchemy on the other hand considers an all-lower case
identifiers to be case insensitive. The Oracle dialect converts identifier to
and from those two formats during schema level communication, such as reflection
of tables and indexes.

It is recommended to work with all lowercase identifiers on the SQLAlchemy side.
These are treated as case insensitve identifiers by SQLAlchemy. The EXASol
dialect takes care of converting them to the internal case insensitive
representation (all uppercase).

"""

import six
if six.PY3:
    from six import u as unicode
from decimal import Decimal
from sqlalchemy import sql, schema, types as sqltypes, util, event
from sqlalchemy.schema import AddConstraint, ForeignKeyConstraint
from sqlalchemy.engine import default, reflection
from sqlalchemy.sql import compiler
from sqlalchemy.sql.elements import quoted_name
from datetime import date, datetime
from .constraints import DistributeByConstraint
import re

AUTOCOMMIT_REGEXP = re.compile(
            r'\s*(?:UPDATE|INSERT|CREATE|DELETE|DROP|ALTER|TRUNCATE)',
                re.I | re.UNICODE)

RESERVED_WORDS = set([ 'absolute', 'action', 'add', 'after', 'all', 'allocate',
'alter', 'and', 'any', 'append', 'are', 'array', 'as', 'asc', 'asensitive',
'assertion', 'at', 'attribute', 'authid', 'authorization', 'before', 'begin',
'between', 'bigint', 'binary', 'bit', 'blob', 'blocked', 'bool', 'boolean',
'both', 'by', 'byte', 'call', 'called', 'cardinality', 'cascade', 'cascaded',
'case', 'casespecific', 'cast', 'catalog', 'chain', 'char', 'character',
'character_set_catalog', 'character_set_name', 'character_set_schema',
'characteristics', 'check', 'checked', 'clob', 'close', 'coalesce', 'collate',
'collation', 'collation_catalog', 'collation_name', 'collation_schema',
'column', 'commit', 'condition', 'connect_by_iscycle', 'connect_by_isleaf',
'connect_by_root', 'connection', 'constant', 'constraint',
'constraint_state_default', 'constraints', 'constructor', 'contains',
'continue', 'control', 'convert', 'corresponding', 'create', 'cs', 'csv',
'cube', 'current', 'current_date', 'current_path', 'current_role',
'current_schema', 'current_session', 'current_statement', 'current_time',
'current_timestamp', 'current_user', 'cursor', 'cycle', 'data', 'datalink',
'date', 'datetime_interval_code', 'datetime_interval_precision', 'day',
'dbtimezone', 'deallocate', 'dec', 'decimal', 'declare', 'default',
'default_like_escape_character', 'deferrable', 'deferred', 'defined',
'definer', 'delete', 'deref', 'derived', 'desc', 'describe', 'descriptor',
'deterministic', 'disable', 'disabled', 'disconnect', 'dispatch', 'distinct',
'dlurlcomplete', 'dlurlpath', 'dlurlpathonly', 'dlurlscheme', 'dlurlserver',
'dlvalue', 'do', 'domain', 'double', 'drop', 'dynamic', 'dynamic_function',
'dynamic_function_code', 'each', 'else', 'elseif', 'elsif', 'emits', 'enable',
'enabled', 'end', 'end-exec', 'enforce', 'equals', 'errors', 'escape',
'except', 'exception', 'exec', 'execute', 'exists', 'exit', 'export',
'external', 'extract', 'false', 'fbv', 'fetch', 'file', 'final', 'first',
'float', 'following', 'for', 'forall', 'force', 'format', 'found', 'free',
'from', 'fs', 'full', 'function', 'general', 'generated', 'geometry', 'get',
'global', 'go', 'goto', 'grant', 'granted', 'group', 'group_concat',
'grouping', 'having', 'high', 'hold', 'hour', 'identity', 'if', 'ifnull',
'immediate', 'implementation', 'import', 'in', 'index', 'indicator', 'inner',
'inout', 'input', 'insensitive', 'insert', 'instance', 'instantiable', 'int',
'integer', 'integrity', 'intersect', 'interval', 'into', 'inverse', 'invoker',
'is', 'iterate', 'join', 'key_member', 'key_type', 'large', 'last', 'lateral',
'ldap', 'leading', 'leave', 'left', 'level', 'like', 'limit', 'local',
'localtime', 'localtimestamp', 'locator', 'log', 'longvarchar', 'loop', 'low',
'map', 'match', 'matched', 'merge', 'method', 'minus', 'minute', 'mod',
'modifies', 'modify', 'module', 'month', 'names', 'national', 'natural',
'nchar', 'nclob', 'new', 'next', 'nls_date_format', 'nls_date_language',
'nls_first_day_of_week', 'nls_numeric_characters', 'nls_timestamp_format',
'no', 'nocycle', 'nologging', 'none', 'not', 'null', 'nullif', 'number',
'numeric', 'nvarchar', 'nvarchar2', 'object', 'of', 'off', 'old', 'on', 'only',
'open', 'option', 'options', 'or', 'order', 'ordering', 'ordinality', 'others',
'out', 'outer', 'output', 'over', 'overlaps', 'overlay', 'overriding', 'pad',
'parallel_enable', 'parameter', 'parameter_specific_catalog',
'parameter_specific_name', 'parameter_specific_schema', 'partial', 'path',
'permission', 'placing', 'plus', 'position', 'preceding', 'preferring',
'prepare', 'preserve', 'prior', 'privileges', 'procedure', 'profile', 'random',
'range', 'read', 'reads', 'real', 'recovery', 'recursive', 'ref', 'references',
'referencing', 'refresh', 'regexp_like', 'relative', 'release', 'rename',
'repeat', 'replace', 'restore', 'restrict', 'result', 'return',
'returned_length', 'returned_octet_length', 'returns', 'revoke', 'right',
'rollback', 'rollup', 'routine', 'row', 'rows', 'rowtype', 'savepoint',
'schema', 'scope', 'script', 'scroll', 'search', 'second', 'section',
'security', 'select', 'selective', 'self', 'sensitive', 'separator',
'sequence', 'session', 'session_user', 'sessiontimezone', 'set', 'sets',
'shortint', 'similar', 'smallint', 'some', 'source', 'space', 'specific',
'specifictype', 'sql', 'sql_bigint', 'sql_bit', 'sql_char', 'sql_date',
'sql_decimal', 'sql_double', 'sql_float', 'sql_integer', 'sql_longvarchar',
'sql_numeric', 'sql_preprocessor_script', 'sql_real', 'sql_smallint',
'sql_timestamp', 'sql_tinyint', 'sql_type_date', 'sql_type_timestamp',
'sql_varchar', 'sqlexception', 'sqlstate', 'sqlwarning', 'start', 'state',
'statement', 'static', 'structure', 'style', 'substring', 'subtype', 'sysdate',
'system', 'system_user', 'systimestamp', 'table', 'temporary', 'text', 'then',
'time', 'timestamp', 'timezone_hour', 'timezone_minute', 'tinyint', 'to',
'trailing', 'transaction', 'transform', 'transforms', 'translation', 'treat',
'trigger', 'trim', 'true', 'truncate', 'under', 'union', 'unique', 'unknown',
'unlink', 'unnest', 'until', 'update', 'usage', 'user', 'using', 'value',
'values', 'varchar', 'varchar2', 'varray', 'verify', 'view', 'when',
'whenever', 'where', 'while', 'window', 'with', 'within', 'without', 'work',
'year', 'yes', 'zone' ])

colspecs = {
}

ischema_names = {
    'BOOLEAN': sqltypes.BOOLEAN,
    'CHAR': sqltypes.CHAR,
    'CLOB': sqltypes.TEXT,
    'DATE': sqltypes.DATE,
    'DECIMAL': sqltypes.DECIMAL,
    'DOUBLE': sqltypes.FLOAT,  # EXASOL mapps DOUBLE, DOUBLE PRECISION, FLOAT to DOUBLE PRECISION
                                 # internally but returns 'DOUBLE' as type when asking the DB catalog
    # INTERVAL DAY [(p)] TO SECOND [(fp)] TODO: missing support for EXA Datatype, check Oracle Engine
    # INTERVAL YEAR[(p)] TO MONTH         TODO: missing support for EXA Datatype, check Oracle Engine
    'TIMESTAMP': sqltypes.TIMESTAMP,
    'VARCHAR': sqltypes.VARCHAR,
}


class EXACompiler(compiler.SQLCompiler):
    extract_map = util.update_copy(
        compiler.SQLCompiler.extract_map,
        {
        'month': '%m',
        'day': '%d',
        'year': '%Y',
        'second': '%S',
        'hour': '%H',
        'doy': '%j',
        'minute': '%M',
        'epoch': '%s',
        'dow': '%w',
        'week': '%W'
    })

    def visit_now_func(self, fn, **kw):
        return "CURRENT_TIMESTAMP"

    def visit_char_length_func(self, fn, **kw):
        return "length%s" % self.function_argspec(fn)

    def limit_clause(self, select, **kw):
        text = ""
        if select._limit is not None:
            text += "\n LIMIT %d" % int(select._limit)
        if select._offset is not None:
            #if self.root_connection.dialect.server_version_info < (5, 0, 0):
            #    util.warn("EXASolution does not support OFFSET")
            #else:
            text += "\n OFFSET %d" % int(select._offset)

        return text

    def for_update_clause(self, select):
        # Exasol has no "FOR UPDATE"
        util.warn("EXASolution does not support SELECT ... FOR UPDATE")
        return ''

    def default_from(self):
        """Called when a ``SELECT`` statement has no froms,
        and no ``FROM`` clause is to be appended.
        """
        return " FROM DUAL"


class EXADDLCompiler(compiler.DDLCompiler):

    def get_column_specification(self, column, **kwargs):
        colspec = self.preparer.format_column(column)
        colspec += " " + self.dialect.type_compiler.process(column.type)
        if column is column.table._autoincrement_column and \
            True and \
            (
                column.default is None or \
                isinstance(column.default, schema.Sequence)
            ):
            colspec += " IDENTITY"
            if isinstance(column.default, schema.Sequence) and \
                column.default.start > 0:
                colspec += " " + str(column.default.start)
        else:
            default = self.get_column_default_string(column)
            if default is not None:
                colspec += " DEFAULT " + default

        if not column.nullable:
            colspec += " NOT NULL"
        return colspec

    def create_table_constraints(self, table, _include_foreign_key_constraints=None):
        # EXASOL does not support FK constraints that reference
        # the table being created. Thus, these need to be created
        # via ALTER TABLE after table creation
        # TODO: FKs that reference other tables could be inlined
        # the create rule could be more specific but for now, ALTER
        # TABLE for all FKs work.
        for c in [c for c in table._sorted_constraints if isinstance(c, ForeignKeyConstraint)]:
            c._create_rule = lambda: False
            event.listen(table, "after_create", AddConstraint(c))
        return super(EXADDLCompiler, self).create_table_constraints(table)

    def visit_add_constraint(self, create):
        if isinstance(create.element, DistributeByConstraint):
            return "ALTER TABLE %s %s" %(
                        self.preparer.format_table(create.element.table),
                        self.process(create.element)
                    )
        else:
            return super(EXADDLCompiler, self).visit_add_constraint(create)

    def visit_drop_constraint(self, drop):
        if isinstance(drop.element, DistributeByConstraint):
            return "ALTER TABLE %s DROP DISTRIBUTION KEYS" % (
                self.preparer.format_table(drop.element.table))
        else:
            return super(EXADDLCompiler, self).visit_drop_constraint(drop)

    def visit_distribute_by_constraint(self, constraint):
        return "DISTRIBUTE BY " + ",".join(c.name for c in constraint.columns)

    def define_constraint_remote_table(self, constraint, table, preparer):
        """Format the remote table clause of a CREATE CONSTRAINT clause."""
        return preparer.format_table(table, use_schema=True)

    def visit_create_index(self, create):
        """EXASol manages indexes internally"""
        raise NotImplementedError()

    def visit_drop_index(self, drop):
        """EXASol manages indexes internally"""
        raise NotImplementedError()


class EXATypeCompiler(compiler.GenericTypeCompiler):

    def visit_large_binary(self, type_):
        return self.visit_BLOB(type_)

    def visit_datetime(self, type_):
        return self.visit_TIMESTAMP(type_)


class EXAIdentifierPreparer(compiler.IdentifierPreparer):
    reserved_words = RESERVED_WORDS
    illegal_initial_characters = compiler.ILLEGAL_INITIAL_CHARACTERS.union('_')

class EXAExecutionContext(default.DefaultExecutionContext):

    def fire_sequence(self, default, type_):
        raise NotImplemented

    def get_insert_default(self, column):
        if column.default.is_sequence:
            return 'DEFAULT'
        else:
            return super(EXAExecutionContext, self).get_insert_default(column)

    def get_lastrowid(self):
        columns = self.compiled.sql_compiler.statement.table.columns
        autoinc_pk_columns = \
            [c.name for c in columns if c.autoincrement and c.primary_key]
        if len(autoinc_pk_columns) == 0:
            return None
        elif len(autoinc_pk_columns) > 1:
            util.warn("Table with more than one autoincrement, primary key"\
                       " Column!")
            raise Exception
        else:
            id_col = self.dialect.denormalize_name(autoinc_pk_columns[0])

            table = self.compiled.sql_compiler.statement.table.name
            table = self.dialect.denormalize_name(table)

            sql_stmnt = "SELECT column_identity from SYS.EXA_ALL_COLUMNS "\
                        "WHERE column_object_type = 'TABLE' and column_table "\
                        "= ? AND column_name = ?"

            schema = self.compiled.sql_compiler.statement.table.schema
            if schema is not None:
                schema = self.dialect.denormalize_name(schema)
                sql_stmnt += " AND column_schema = ?"

            cursor = self.create_cursor()
            if schema:
                cursor.execute(sql_stmnt, (table, id_col, schema))
            else:
                cursor.execute(sql_stmnt, (table, id_col))
            result = cursor.fetchone()
            cursor.close()
            return int(result[0]) - 1

    def pre_exec(self):
        """
        This routine inserts the parameters into the compiled query prior to executing it.
        The reason for this workaround is the poor performance for prepared statements.
        Note: Parameter replacement is done for server versions < 4.1.8 or
              in case a delete query is executed.
        """
        if self.isdelete or self.root_connection.dialect.server_version_info < (4, 1, 8):
            db_query = self.unicode_statement
            for i in range(1, len(self.parameters)):
                db_query += ", (" + ", ".join(['?'] * len(self.parameters[i])) + ")"
            for db_para in self.parameters:
                for value in db_para:
                    ident = '?'
                    if value is None:
                        db_query = db_query.replace(ident, 'NULL', 1)
                    elif isinstance(value, six.integer_types):
                        db_query = db_query.replace(ident, str(value), 1)
                    elif isinstance(value, (float, Decimal)):
                        db_query = db_query.replace(ident, str(float(value)), 1)
                    elif isinstance(value, bool):
                        db_query = db_query.replace(ident, '1' if value else '0', 1)
                    elif isinstance(value, datetime):
                        db_query = db_query.replace(ident, "to_timestamp('%s', 'YYYY-MM-DD HH24:MI:SS.FF6')" % value.strftime('%Y-%m-%d %H:%M:%S.%f'), 1)
                    elif isinstance(value, date):
                        db_query = db_query.replace(ident, "to_date('%s', 'YYYY-MM-DD')" % value.strftime('%Y-%m-%d'), 1)
                    elif isinstance(value, six.binary_type):
                        db_query = db_query.replace(ident, "'%s'" % value.decode('UTF-8'), 1)
                    elif isinstance(value, six.text_type):
                        db_query = db_query.replace(ident, "'%s'" % value, 1)
                    else:
                        raise TypeError('Data type not supported: %s' % type(value))
            self.statement = db_query
            self.parameters = [[]]

    def should_autocommit_text(self, statement):
        return AUTOCOMMIT_REGEXP.match(statement)

class EXADialect(default.DefaultDialect):
    name = 'exasol'
    supports_native_boolean = True
    supports_native_decimal = True
    supports_alter = True
    supports_unicode_statements = True
    supports_unicode_binds = True
    supports_default_values = True
    supports_empty_insert = False
    supports_sequences = False
    # sequences_optional = True
    # controls in SQLAlchemy base which columns are part of an insert statement
    # postfetch_lastrowid = True
    supports_cast = True
    requires_name_normalize = True

    default_paramstyle = 'qmark'
    execution_ctx_cls = EXAExecutionContext
    statement_compiler = EXACompiler
    ddl_compiler = EXADDLCompiler
    type_compiler = EXATypeCompiler
    preparer = EXAIdentifierPreparer
    ischema_names = ischema_names
    colspecs = colspecs
    isolation_level = None

    def __init__(self, isolation_level=None, native_datetime=False, **kwargs):
        default.DefaultDialect.__init__(self, **kwargs)
        self.isolation_level = isolation_level

    _isolation_lookup = {
        'SERIALIZABLE': 0
    }

    def _get_default_schema_name(self, connection):
        """
        Default schema is derived from current connections url
        or 'SYS'. Tables in 'SYS' are not reflectable!
        """
        schema = None
        if connection.engine.url is not None:
            schema = self.normalize_name(
                    connection.engine.url.translate_connect_args().get('database'))
        if schema is None:
            schema = self.normalize_name(u"SYS")
        return schema

    def normalize_name(self, name):
        """
        Converting EXASol case insensitive identifiers (upper case)
        to  SQLAlchemy case insensitive identifiers (lower case)
        """
        if name is None:
            return None

        if six.PY2:
            if isinstance(name, str):
                name = name.decode(self.encoding)

        if name.upper() == name and \
              not self.identifier_preparer._requires_quotes(name.lower()):
            return name.lower()
        elif name.lower() == name:
            return quoted_name(name, quote=True)
        else:
            return name

    def denormalize_name(self, name):
        """
        Converting SQLAlchemy case insensitive identifiers (lower case)
        to  EXASol case insensitive identifiers (upper case)
        """
        if name is None or len(name) == 0:
            return None
        elif name.lower() == name and \
                not self.identifier_preparer._requires_quotes(name.lower()):
            name = name.upper()

        if six.PY2:
            if not self.supports_unicode_binds:
                name = name.encode(self.encoding)
            else:
                name = unicode(name)

        return name

    def get_isolation_level(self, connection):
        return "SERIALIZABLE"

    def on_connect(self):
        # TODO: set isolation level
        pass

    # never called during reflection
    @reflection.cache
    def get_schema_names(self, connection, **kw):
        sql_stmnt = "select SCHEMA_NAME from SYS.EXA_SCHEMAS"
        rs = connection.execute(sql.text(sql_stmnt))
        return [self.normalize_name(row[0]) for row in rs]

    @reflection.cache
    def get_table_names(self, connection, schema, **kw):
        schema = self.denormalize_name(schema or
                connection.engine.url.database)
        sql_stmnt = "SELECT table_name FROM  SYS.EXA_ALL_TABLES WHERE table_schema = "
        if schema is None:
            sql_stmnt += "CURRENT_SCHEMA ORDER BY table_name"
            rs = connection.execute(sql_stmnt)
        else:
            sql_stmnt += ":schema ORDER BY table_name"
            rs = connection.execute(sql.text(sql_stmnt), \
                schema=self.denormalize_name(schema))
        return [self.normalize_name(row[0]) for row in rs]

    def has_table(self, connection, table_name, schema=None):
        schema = schema or connection.engine.url.database
        sql_stmnt = "SELECT table_name from SYS.EXA_ALL_TABLES "\
                    "WHERE table_name = :table_name "
        if schema is not None:
            sql_stmnt += "AND table_schema = :schema"
        rp = connection.execute(
                sql.text(sql_stmnt),
                table_name=self.denormalize_name(table_name),
                schema=self.denormalize_name(schema))
        row = rp.fetchone()

        return (row is not None)

    @reflection.cache
    def get_view_names(self, connection, schema=None, **kw):
        schema = schema or connection.engine.url.database
        sql_stmnt = "SELECT view_name FROM  SYS.EXA_ALL_VIEWS WHERE view_schema = "
        if schema is None:
            sql_stmnt += "CURRENT_SCHEMA ORDER BY view_name"
            rs = connection.execute(sql.text(sql_stmnt))
        else:
            sql_stmnt += ":schema ORDER BY view_name"
            rs = connection.execute(sql.text(sql_stmnt),
                schema=self.denormalize_name(schema))
        return [self.normalize_name(row[0]) for row in rs]

    @reflection.cache
    def get_view_definition(self, connection, view_name, schema=None, **kw):
        schema = schema or connection.engine.url.database
        sql_stmnt = "SELECT view_text FROM sys.exa_all_views WHERE view_name = :view_name AND view_schema = "
        if schema is None:
            sql_stmnt += "CURRENT_SCHEMA"
        else:
            sql_stmnt += ":schema"
        rp = connection.execute(sql.text(sql_stmnt),
                view_name=self.denormalize_name(view_name),
                schema=self.denormalize_name(schema)).scalar()
        if rp:
            if six.PY3:
                return rp
            else:
                return rp.decode(self.encoding)
        else:
            return None


    @reflection.cache
    def _get_all_columns(self, connection, schema=None, **kw):
        sql_stmnt = "SELECT column_name, column_type, column_maxsize, column_num_prec, column_num_scale, " \
                    "column_is_nullable, column_default, column_identity, column_is_distribution_key, column_table " \
                    "FROM sys.exa_all_columns  WHERE column_object_type IN ('TABLE', 'VIEW') " \
                    "AND column_schema = "

        if schema is None:
            sql_stmnt += "CURRENT_SCHEMA "
        else:
            sql_stmnt += ":schema "
        sql_stmnt += "ORDER BY column_ordinal_position"
        rp = connection.execute(sql.text(sql_stmnt),
                schema=self.denormalize_name(schema))

        return list(rp)


    @reflection.cache
    def get_columns(self, connection, table_name, schema=None, **kw):
        schema = schema or connection.engine.url.database
        if schema is None:
            schema = connection.execute("select CURRENT_SCHEMA from dual").scalar()
        table_name=self.denormalize_name(table_name)
        schema=self.denormalize_name(schema)

        columns = []
        for row in self._get_all_columns(connection, schema, info_cache=kw.get("info_cache")):
            if row[9] != table_name and table_name is not None:
                continue
            (colname, coltype, length, precision, scale, nullable, default, identity, is_distribution_key) = \
                (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])

            # FIXME: Missing type support: INTERVAL DAY [(p)] TO SECOND [(fp)], INTERVAL YEAR[(p)] TO MONTH

            # remove ASCII, UTF8 and spaces from char-like types
            coltype = re.sub(r'ASCII|UTF8| ', '', coltype)
            # remove precision and scale addition from numeric types
            coltype = re.sub(r'\(\d+(\,\d+)?\)', '', coltype)
            try:
                if coltype == 'VARCHAR':
                    coltype = sqltypes.VARCHAR(length)
                elif coltype == 'DECIMAL':
                    # this Dialect forces INTTYPESINRESULTSIFPOSSIBLE=y on ODBC level
                    # thus, we need to convert DECIMAL(<=18,0) back to INTEGER type
                    if scale == 0 and precision <= 18:
                        coltype = sqltypes.INTEGER()
                    else:
                        coltype = sqltypes.DECIMAL(precision, scale)
                else:
                    coltype = self.ischema_names[coltype]
            except KeyError:
                util.warn("Did not recognize type '%s' of column '%s'" %
                          (coltype, colname))
                coltype = sqltypes.NULLTYPE

            cdict = {
                'name': self.normalize_name(colname),
                'type': coltype,
                'nullable': nullable,
                'default': default,
                'is_distribution_key': is_distribution_key
            }
            if identity:
                identity = int(identity)
            # if we have a positive identity value add a sequence
            if identity is not None and identity >= 0:
                cdict['sequence'] = {'name':''}
                # TODO: we have to possibility to encode the current identity value count
                # into the column metadata. But the consequence is that it would also be used
                # as start value in CREATE statements. For now the current value is ignored.
                # Add it by changing the dict to: {'name':'', 'start': int(identity)}
            columns.append(cdict)
        return columns

    @reflection.cache
    def _get_all_constraints(self, connection, schema=None, **kw):
        sql_stmnt = "SELECT constraint_name, column_name, referenced_schema, referenced_table, " \
                     "referenced_column, constraint_table, constraint_type " \
                     "FROM SYS.EXA_ALL_CONSTRAINT_COLUMNS where constraint_schema = "

        if schema is None:
            sql_stmnt += "CURRENT_SCHEMA "
        else:
            sql_stmnt += ":schema "
        sql_stmnt += "ORDER BY ordinal_position"
        rp = connection.execute(sql.text(sql_stmnt),
                schema=self.denormalize_name(schema))

        return list(rp)


    @reflection.cache
    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
        schema = schema or connection.engine.url.database
        pkeys = []
        constraint_name = None
        table_name=self.denormalize_name(table_name)

        for row in self._get_all_constraints(connection, schema, info_cache=kw.get("info_cache")):
            if (row[5] != table_name and table_name is not None) or row[6] != 'PRIMARY KEY':
                continue
            pkeys.append(self.normalize_name(row[1]))
            constraint_name = self.normalize_name(row[0])
        return {'constrained_columns': pkeys, 'name': constraint_name}

    @reflection.cache
    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        schema_int = schema or connection.engine.url.database
        if schema_int is None:
            schema_int = connection.execute("select CURRENT_SCHEMA from dual").scalar()
        table_name=self.denormalize_name(table_name)
        def fkey_rec():
            return {
                'name': None,
                'constrained_columns': [],
                'referred_schema': None,
                'referred_table': None,
                'referred_columns': []
            }

        fkeys = util.defaultdict(fkey_rec)

        for row in self._get_all_constraints(connection, schema=schema, info_cache=kw.get("info_cache")):
            if (row[5] != table_name and table_name is not None) or row[6] != 'FOREIGN KEY':
                continue
            (cons_name, local_column, remote_schema, remote_table, remote_column) = \
                    (row[0], row[1], row[2], row[3], row[4])
            rec = fkeys[self.normalize_name(cons_name)]
            rec['name'] = self.normalize_name(cons_name)
            local_cols, remote_cols = rec['constrained_columns'], rec['referred_columns']

            if not rec['referred_table']:
                rec['referred_table'] = self.normalize_name(remote_table)
                # we need to take care of calls without schema. the sqla test suite
                # expects referred_schema to be None if None is passed in to this function
                if schema is None and self.normalize_name(schema_int) == self.normalize_name(remote_schema):
                    rec['referred_schema'] = None
                else:
                    rec['referred_schema'] = self.normalize_name(remote_schema)

            local_cols.append(self.normalize_name(local_column))
            remote_cols.append(self.normalize_name(remote_column))

        return list(fkeys.values())

    @reflection.cache
    def get_indexes(self, connection, table_name, schema=None, **kw):
        schema = schema or connection.engine.url.database
        # EXASolution has no indexes
        # TODO: check if indexes are used by SQLA for optimizing SQL Statements.
        # If so, we should return all columns as being indexed
        return []
