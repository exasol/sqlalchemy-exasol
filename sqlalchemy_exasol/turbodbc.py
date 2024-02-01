import decimal
from warnings import warn

from sqlalchemy import types as sqltypes
from sqlalchemy import util

from sqlalchemy_exasol.base import EXADialect
from sqlalchemy_exasol.warnings import SqlaExasolDeprecationWarning

DEFAULT_CONNECTION_PARAMS = {
    # always enable efficient conversion to Python types:
    # see https://www.exasol.com/support/browse/EXASOL-898
    "inttypesinresultsifpossible": "y",
}

DEFAULT_TURBODBC_PARAMS = {"read_buffer_size": 50}

TURBODBC_TRANSLATED_PARAMS = {
    "read_buffer_size",
    "parameter_sets_to_buffer",
    "use_async_io",
    "varchar_max_character_limit",
    "prefer_unicode",
    "large_decimals_as_64_bit_types",
    "limit_varchar_results_to_max",
    "autocommit",
}


class _ExaDecimal(sqltypes.DECIMAL):
    def bind_processor(self, dialect):
        return super().bind_processor(dialect)

    def result_processor(self, dialect, coltype):
        if self.asdecimal:
            fstring = "%%.%df" % self._effective_decimal_return_scale

            def to_decimal(value):
                if value is None:
                    return None
                elif isinstance(value, decimal.Decimal):
                    return value
                elif isinstance(value, float):
                    return decimal.Decimal(fstring % value)
                else:
                    return decimal.Decimal(value)

            return to_decimal
        else:
            return None


class _ExaInteger(sqltypes.INTEGER):
    def bind_processor(self, dialect):
        return super().bind_processor(dialect)

    def result_processor(self, dialect, coltype):
        def to_integer(value):
            # cast if turbodbc returns a VARCHAR
            if coltype == 30:
                return int(value)
            else:
                return value

        return to_integer


class EXADialect_turbodbc(EXADialect):
    driver = "turbodbc"
    driver_version = None
    supports_statement_cache = False
    supports_native_decimal = False
    supports_sane_multi_rowcount = False

    colspecs = {sqltypes.Numeric: _ExaDecimal, sqltypes.Integer: _ExaInteger}

    def __init__(self, **kw):
        message = (
            "'turbodbc' support in 'sqlalchemy_exasol' is deprecated and will be removed. "
            "Please switch to the websocket driver. See documentation for details."
        )
        warn(message, SqlaExasolDeprecationWarning)
        super().__init__(**kw)

    @classmethod
    def dbapi(cls):
        return __import__("turbodbc")

    def create_connect_args(self, url):
        options = self._get_options_with_defaults(url)
        self._translate_none(options)
        self._interpret_destination(options)

        return [[options.pop("dsn", None)], options]

    @staticmethod
    def _get_options_with_defaults(url):
        user_options = url.translate_connect_args(
            username="uid", password="pwd", database="exaschema", host="destination"
        )
        user_options.update(url.query)

        options = {
            key.lower(): value for (key, value) in DEFAULT_CONNECTION_PARAMS.items()
        }
        options.update(
            {key.lower(): value for (key, value) in DEFAULT_TURBODBC_PARAMS.items()}
        )
        for key in user_options.keys():
            options[key.lower()] = user_options[key]

        real_turbodbc = __import__("turbodbc")
        turbodbc_options = {}
        for param in TURBODBC_TRANSLATED_PARAMS:
            if param in options:
                raw = options.pop(param)
                if param in {
                    "use_async_io",
                    "prefer_unicode",
                    "large_decimals_as_64_bit_types",
                    "limit_varchar_results_to_max",
                    "autocommit",
                }:
                    value = util.asbool(raw)
                elif param == "read_buffer_size":
                    value = real_turbodbc.Megabytes(util.asint(raw))
                else:
                    value = util.asint(raw)
                turbodbc_options[param] = value

        options["turbodbc_options"] = real_turbodbc.make_options(**turbodbc_options)

        return options

    @staticmethod
    def _interpret_destination(options):
        if ("port" in options) or ("database" in options):
            options["exahost"] = "{}:{}".format(
                options.pop("destination"), options.pop("port")
            )
        else:
            options["dsn"] = options.pop("destination")

    @staticmethod
    def _translate_none(options):
        for key in options:
            if options[key] == "None":
                options[key] = None


dialect = EXADialect_turbodbc
