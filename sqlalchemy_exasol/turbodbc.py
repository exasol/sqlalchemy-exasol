from sqlalchemy import types as sqltypes
from sqlalchemy_exasol.base import EXADialect
import decimal

DEFAULT_DRIVER_NAME = 'EXAODBC'

# EXASOL sometimes gives 2M big text columns, combined with a too big default buffer value
# this could lead to a MemoryError. Because of this we reduce the turbodbc default
DEFAULT_CONNECTION_PARAMS = {
    'rows_to_buffer': 100,
    'driver': DEFAULT_DRIVER_NAME,
    # always enable efficient conversion to Python types: see https://www.exasol.com/support/browse/EXASOL-898
    'INTTYPESINRESULTSIFPOSSIBLE': 'y',
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
        in_opts = url.translate_connect_args(username='user')
        in_opts.update(url.query)

        opts = dict()
        keys = list(in_opts)
        for key in keys:
            opts[key.lower()] = in_opts[key]

        for default_setting in DEFAULT_CONNECTION_PARAMS:
            opts[default_setting] = opts.pop(default_setting,
                                             DEFAULT_CONNECTION_PARAMS[default_setting])
            if opts[default_setting] == 'None':
                opts[default_setting] = None

        if all(key not in opts for key in ['port', 'database']):
            dsn = opts.pop('host')
        else:
            dsn = None

        if 'user' in opts:
            opts['UID'] = opts.pop('user')
        if 'password' in opts:
            opts['PWD'] = opts.pop('password')
        if 'database' in opts:
            opts['EXASCHEMA'] = opts.pop('database')

        if 'host' in opts:
            opts['EXAHOST'] = "{}:{}".format(opts.pop('host'), opts.pop('port'))

        return [[dsn], opts]

    def _get_server_version_info(self, connection):
        if self.server_version_info is None:
            query = "select PARAM_VALUE from SYS.EXA_METADATA where PARAM_NAME = 'databaseProductVersion'"
            result = connection.execute(query).fetchone()[0].split('.')

            # last version position can something like: '12-S'
            self.server_version_info = (int(result[0]), int(result[1]), int(result[2].split('-')[0]))

        return self.server_version_info


dialect = EXADialect_turbodbc
