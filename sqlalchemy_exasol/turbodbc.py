from sqlalchemy import types as sqltypes
from sqlalchemy_exasol.base import EXADialect
import decimal


def _get_default_buffer_size():
    try:
        real_turbodbc = __import__('turbodbc')
        return real_turbodbc.Megabytes(50)
    except ImportError:
        return None


DEFAULT_DRIVER_NAME = 'EXAODBC'

DEFAULT_CONNECTION_PARAMS = {
    'read_buffer_size': _get_default_buffer_size(),
    'driver': DEFAULT_DRIVER_NAME,
    # always enable efficient conversion to Python types: see https://www.exasol.com/support/browse/EXASOL-898
    'inttypesinresultsifpossible': 'y',
}


class _ExaDecimal(sqltypes.DECIMAL):
    def bind_processor(self, dialect):
        return super(_ExaDecimal, self).bind_processor(dialect)

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
        return super(_ExaInteger, self).bind_processor(dialect)

    def result_processor(self, dialect, coltype):
        def to_integer(value):
            # cast if turbodbc returns a VARCHAR
            if coltype == 30:
                return int(value)
            else:
                return value

        return to_integer


class EXADialect_turbodbc(EXADialect):
    driver = 'turbodbc'
    driver_version = None
    server_version_info = None
    supports_native_decimal = False
    supports_sane_multi_rowcount = False

    colspecs = {sqltypes.Numeric: _ExaDecimal, sqltypes.Integer: _ExaInteger}

    @classmethod
    def dbapi(cls):
        return __import__('turbodbc')

    def create_connect_args(self, url):
        options = self._get_options_with_defaults(url)
        self._translate_none(options)
        self._interpret_destination(options)

        return [[options.pop("dsn", None)], options]

    def _get_server_version_info(self, connection):
        if self.server_version_info is None:
            query = "select PARAM_VALUE from SYS.EXA_METADATA where PARAM_NAME = 'databaseProductVersion'"
            result = connection.execute(query).fetchone()[0].split('.')

            # last version position can something like: '12-S'
            self.server_version_info = (int(result[0]), int(result[1]), int(result[2].split('-')[0]))

        return self.server_version_info

    def _get_options_with_defaults(self, url):
        user_options = url.translate_connect_args(username='uid',
                                                  password='pwd',
                                                  database='exaschema',
                                                  host='destination')
        user_options.update(url.query)

        options = {key.lower(): value for (key, value) in DEFAULT_CONNECTION_PARAMS.items()}
        for key in user_options.keys():
            options[key.lower()] = user_options[key]

        return options

    def _interpret_destination(self, options):
        if ('port' in options) or ('database' in options):
            options['exahost'] = "{}:{}".format(options.pop('destination'),
                                                options.pop('port'))
        else:
            options['dsn'] = options.pop('destination')

    def _translate_none(self, options):
        for key in options:
            if options[key] == 'None':
                options[key] = None

dialect = EXADialect_turbodbc
