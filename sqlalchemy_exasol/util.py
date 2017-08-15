import datetime

from sqlalchemy_exasol.pyodbc import EXADialect_pyodbc
from sqlalchemy_exasol import base

def raw_sql(query):
    """
    Converts an SQLAlchemy object to a single raw SQL string. Note
    that this function currently only supports Exasol queries!

    .. note::

        If you want to pass a string to a sqlalchemy connection please use
        :func:`unicode_sql` to handle unicode values correctly.

    :param query: An SQLAlchemy query object

    :returns: A string of raw SQL
    :rtype: string
    """
    dialect = EXADialect_pyodbc()

    class LiteralCompiler(base.EXACompiler):
        def visit_bindparam(self, bindparam,
                            within_columns_clause=False,
                            literal_binds=False, **kwargs):
            return super(LiteralCompiler, self).render_literal_bindparam(
                bindparam, within_columns_clause=within_columns_clause,
                literal_binds=literal_binds, **kwargs)

        def render_literal_value(self, value, type_):
            if value is None:
                return 'NULL'
            elif isinstance(value, str):
                return u"'{value}'".format(value=unicode(value, encoding='utf-8'))
            elif isinstance(value, unicode):
                return u"'{value}'".format(value=value)
            elif type(value) is datetime.date:
                return "to_date('{value}', 'YYYY-MM-DD')"\
                    .format(value=value.strftime('%Y-%m-%d'))
            elif type(value) is datetime.datetime:
                return "to_timestamp('{value}', 'YYYY-MM-DD HH24:MI:SS.FF6')"\
                    .format(value=value.strftime('%Y-%m-%d %H:%M:%S.%f'))
            else:
                return str(value)

    compiler = LiteralCompiler(dialect, query)
    raw_sql_string = compiler.string
    raw_sql_string = raw_sql_string.encode('UTF-8')

    return raw_sql_string
