import datetime

from sqlalchemy_exasol import base
from sqlalchemy_exasol.websocket import EXADialect_websocket


def raw_sql(query):
    """
    Converts an SQLAlchemy object to a single raw SQL string. Note
    that this function currently only supports Exasol queries!

    :param query: An SQLAlchemy query object

    :returns: A string of raw SQL
    :rtype: string
    """
    dialect = EXADialect_websocket()

    class LiteralCompiler(base.EXACompiler):
        def visit_bindparam(
            self, bindparam, within_columns_clause=False, literal_binds=False, **kwargs
        ):
            return super().render_literal_bindparam(
                bindparam,
                within_columns_clause=within_columns_clause,
                literal_binds=literal_binds,
                **kwargs,
            )

        def render_literal_value(self, value, type_):
            if value is None:
                return "NULL"
            if isinstance(value, bytes):
                return "'{value}'".format(value=value.decode("utf-8"))
            if isinstance(value, str):
                return f"'{value}'"
            if type(value) is datetime.date:
                return "to_date('{value}', 'YYYY-MM-DD')".format(
                    value=value.strftime("%Y-%m-%d")
                )
            if type(value) is datetime.datetime:
                return "to_timestamp('{value}', 'YYYY-MM-DD HH24:MI:SS.FF6')".format(
                    value=value.strftime("%Y-%m-%d %H:%M:%S.%f")
                )
            return f"{value}"

    compiler = LiteralCompiler(dialect, query)
    return compiler.string
