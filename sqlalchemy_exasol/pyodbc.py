"""
Connect string::

    exa+pyodbc://<username>:<password>@<dsnname>
    exa+pyodbc://<username>:<password>@<ip_range>:<port>/<schema>?<options>

"""

import logging
import re
import sys
from warnings import warn

from packaging import version
from sqlalchemy import sql
from sqlalchemy.connectors.pyodbc import PyODBCConnector
from sqlalchemy.engine import reflection
from sqlalchemy.util.langhelpers import asbool

from sqlalchemy_exasol.base import (
    EXADialect,
    EXAExecutionContext,
)
from sqlalchemy_exasol.warnings import SqlaExasolDeprecationWarning

logger = logging.getLogger("sqlalchemy_exasol")


class EXADialect_pyodbc(EXADialect, PyODBCConnector):
    supports_statement_cache = False
    execution_ctx_cls = EXAExecutionContext
    driver_version = None

    def __init__(self, **kw):
        message = (
            "'pyodbc' support in 'sqlalchemy_exasol' is deprecated and will be removed. "
            "Please switch to the websocket driver. See documentation for details."
        )
        warn(message, SqlaExasolDeprecationWarning)
        super().__init__(**kw)

    def get_driver_version(self, connection):
        # LooseVersion will also work with interim versions like '4.2.7dev1' or '5.0.rc4'
        if self.driver_version is None:
            self.driver_version = version.parse(
                connection.connection.getinfo(self.dbapi.SQL_DRIVER_VER) or "2.0.0"
            )
        return self.driver_version

    if sys.platform == "darwin":

        def connect(self, *cargs, **cparams):
            # Get connection
            conn = super().connect(*cargs, **cparams)

            # Set up encodings
            conn.setdecoding(self.dbapi.SQL_CHAR, encoding="utf-8")
            conn.setdecoding(self.dbapi.SQL_WCHAR, encoding="utf-8")
            conn.setdecoding(self.dbapi.SQL_WMETADATA, encoding="utf-8")

            conn.setencoding(encoding="utf-8")

            # Return connection
            return conn

    def create_connect_args(self, url):
        """
        Connection strings are EXASolution specific. See EXASolution manual on Connection-String-Parameters.

        `ODBC Driver Settings <https://docs.exasol.com/db/latest/connect_exasol/drivers/odbc/using_odbc.htm>`_
        """
        opts = url.translate_connect_args(username="user")
        opts.update(url.query)
        # always enable efficient conversion to Python types: see https://www.exasol.com/support/browse/EXASOL-898
        opts["INTTYPESINRESULTSIFPOSSIBLE"] = "y"
        # Make sure the exasol odbc driver reports the expected error codes.
        # see also:
        #   * https://docs.exasol.com/db/latest/connect_exasol/drivers/odbc/using_odbc.htm
        #   * https://github.com/exasol/sqlalchemy-exasol/issues/118
        opts["SQLSTATEMAPPINGACTIVE"] = "y"
        opts["SQLSTATEMAPPINGS"] = "42X91:23000,27002:23000"

        keys = opts
        query = url.query

        connect_args = {}
        for param in ("ansi", "unicode_results", "autocommit"):
            if param in keys:
                connect_args[param.upper()] = asbool(keys.pop(param))

        dsn_connection = "dsn" in keys or ("host" in keys and "port" not in keys)
        if dsn_connection:
            connectors = ["DSN=%s" % (keys.pop("dsn", "") or keys.pop("host", ""))]
        else:
            connectors = ["DRIVER={%s}" % keys.pop("driver", None)]

        port = ""
        if "port" in keys and not "port" in query:
            port = ":%d" % int(keys.pop("port"))

        connectors.extend(
            [
                "EXAHOST={}{}".format(keys.pop("host", ""), port),
                "EXASCHEMA=%s" % keys.pop("database", ""),
            ]
        )

        user = keys.pop("user", None)
        if user:
            connectors.append("UID=%s" % user)
            connectors.append("PWD=%s" % keys.pop("password", ""))
        else:
            connectors.append("Trusted_Connection=Yes")

        # if set to 'Yes', the ODBC layer will try to automagically
        # convert textual data from your database encoding to your
        # client encoding.  This should obviously be set to 'No' if
        # you query a cp1253 encoded database from a latin1 client...
        if "odbc_autotranslate" in keys:
            connectors.append("AutoTranslate=%s" % keys.pop("odbc_autotranslate"))

        connectors.extend([f"{k}={v}" for k, v in sorted(keys.items())])
        return [[";".join(connectors)], connect_args]

    def is_disconnect(self, e, connection, cursor):
        if isinstance(e, self.dbapi.Error):
            error_codes = {
                "40004",  # Connection lost.
                "40009",  # Connection lost after internal server error.
                "40018",  # Connection lost after system running out of memory.
                "40020",  # Connection lost after system running out of memory.
            }
            exasol_error_codes = {
                "HY000": (  # Generic Exasol error code
                    re.compile(r"operation timed out", re.IGNORECASE),
                    re.compile(r"connection lost", re.IGNORECASE),
                    re.compile(r"Socket closed by peer", re.IGNORECASE),
                )
            }

            error_code, error_msg = e.args[:2]

            # import pdb; pdb.set_trace()
            if error_code in exasol_error_codes:
                # Check exasol error
                for msg_re in exasol_error_codes[error_code]:
                    if msg_re.search(error_msg):
                        return True

                return False

            # Check Pyodbc error
            return error_code in error_codes

        return super().is_disconnect(e, connection, cursor)

    @staticmethod
    def _is_sql_fallback_requested(**kwargs):
        is_fallback_requested = kwargs.get("use_sql_fallback", False)
        if is_fallback_requested:
            logger.warning("Using sql fallback instead of odbc functions")
        return is_fallback_requested

    @staticmethod
    def _dbapi_connection(connection):
        return connection.connection.driver_connection

    @reflection.cache
    def _tables_for_schema(self, connection, schema, table_type=None, table_name=None):
        schema = self._get_schema_for_input_or_current(connection, schema)
        table_name = self.denormalize_name(table_name)
        conn = self._dbapi_connection(connection)
        with conn.cursor().tables(
            schema=schema, tableType=table_type, table=table_name
        ) as table_cursor:
            return [row for row in table_cursor]

    @reflection.cache
    def get_view_definition(self, connection, view_name, schema=None, **kw):
        if self._is_sql_fallback_requested(**kw):
            return super().get_view_definition(connection, view_name, schema, **kw)
        if view_name is None:
            return None

        tables = self._tables_for_schema(
            connection, schema, table_type="VIEW", table_name=view_name
        )
        if len(tables) != 1:
            return None

        quoted_view_name_string = self.quote_string_value(tables[0][2])
        quoted_view_schema_string = self.quote_string_value(tables[0][1])
        sql_statement = (
            "/*snapshot execution*/ SELECT view_text "
            f"FROM sys.exa_all_views WHERE view_name = {quoted_view_name_string} "
            f"AND view_schema = {quoted_view_schema_string}"
        )
        result = connection.execute(sql.text(sql_statement)).scalar()
        return result if result else None

    @reflection.cache
    def get_table_names(self, connection, schema, **kw):
        if self._is_sql_fallback_requested(**kw):
            return super().get_table_names(connection, schema, **kw)
        tables = self._tables_for_schema(connection, schema, table_type="TABLE")
        return [self.normalize_name(row.table_name) for row in tables]

    @reflection.cache
    def get_view_names(self, connection, schema=None, **kw):
        if self._is_sql_fallback_requested(**kw):
            return super().get_view_names(connection, schema, **kw)
        tables = self._tables_for_schema(connection, schema, table_type="VIEW")
        return [self.normalize_name(row.table_name) for row in tables]

    def has_table(self, connection, table_name, schema=None, **kw):
        if self._is_sql_fallback_requested(**kw):
            return super().has_table(connection, table_name, schema, **kw)
        tables = self.get_table_names(
            connection=connection, schema=schema, table_name=table_name, **kw
        )
        return self.normalize_name(table_name) in tables

    def _get_schema_names_query(self, connection, **kw):
        if self._is_sql_fallback_requested(**kw):
            return super()._get_schema_names_query(connection, **kw)
        return "/*snapshot execution*/ " + super()._get_schema_names_query(
            connection, **kw
        )

    @reflection.cache
    def _get_columns(self, connection, table_name, schema=None, **kw):
        if self._is_sql_fallback_requested(**kw):
            return super()._get_columns(connection, table_name, schema, **kw)

        tables = self._tables_for_schema(
            connection, schema=schema, table_name=table_name
        )
        if len(tables) != 1:
            return []

        # get_columns_sql originally returned all columns of all tables if table_name is None,
        # we follow this behavior here for compatibility. However, the documentation for Dialects
        # does not mention this behavior:
        # https://docs.sqlalchemy.org/en/13/core/internals.html#sqlalchemy.engine.interfaces.Dialect
        quoted_schema_string = self.quote_string_value(tables[0].table_schem)
        quoted_table_string = self.quote_string_value(tables[0].table_name)
        sql_statement = "/*snapshot execution*/ {query}".format(
            query=self.get_column_sql_query_str()
        )
        sql_statement = sql_statement.format(
            schema=quoted_schema_string, table=quoted_table_string
        )
        response = connection.execute(sql.text(sql_statement))

        return list(response)

    @reflection.cache
    def _get_pk_constraint(self, connection, table_name, schema=None, **kw):
        if self._is_sql_fallback_requested(**kw):
            return super()._get_pk_constraint(connection, table_name, schema, **kw)

        conn = self._dbapi_connection(connection)
        schema = self._get_schema_for_input_or_current(connection, schema)
        table_name = self.denormalize_name(table_name)
        with conn.cursor().primaryKeys(table=table_name, schema=schema) as cursor:
            pkeys = []
            constraint_name = None
            for row in cursor:
                table, primary_key, constraint = row[2], row[3], row[5]
                if table != table_name and table_name is not None:
                    continue
                pkeys.append(self.normalize_name(primary_key))
                constraint_name = self.normalize_name(constraint)
        return {"constrained_columns": pkeys, "name": constraint_name}

    @reflection.cache
    def _get_foreign_keys(self, connection, table_name, schema=None, **kw):
        if self._is_sql_fallback_requested(**kw):
            return super()._get_foreign_keys(connection, table_name, schema, **kw)

        # Need to use a workaround, because SQLForeignKeys functions doesn't work for an unknown reason
        tables = self._tables_for_schema(
            connection=connection,
            schema=schema,
            table_name=table_name,
            table_type="TABLE",
        )
        if len(tables) == 0:
            return []

        quoted_schema_string = self.quote_string_value(tables[0].table_schem)
        quoted_table_string = self.quote_string_value(tables[0].table_name)
        sql_statement = "/*snapshot execution*/ {query}".format(
            query=self._get_constraint_sql_str(
                quoted_schema_string, quoted_table_string, "FOREIGN KEY"
            )
        )
        response = connection.execute(sql.text(sql_statement))

        return list(response)


dialect = EXADialect_pyodbc
