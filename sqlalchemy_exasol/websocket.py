import datetime
import decimal
import time
from collections import (
    defaultdict,
    namedtuple,
)

from sqlalchemy.sql import sqltypes

from sqlalchemy_exasol.base import EXADialect


class Integer(sqltypes.INTEGER):
    def result_processor(self, dialect, coltype):
        def to_integer(value):
            if isinstance(value, str):
                return int(value)
            return value

        return to_integer


class Decimal(sqltypes.DECIMAL):
    def bind_processor(self, dialect):
        return super().bind_processor(dialect)

    def result_processor(self, dialect, coltype):
        if not self.asdecimal:
            return None

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


class Date(sqltypes.DATE):
    def bind_processor(self, dialect):
        return super().bind_processor(dialect)

    def result_processor(self, dialect, coltype):
        def to_date(value):
            if not isinstance(value, str):
                return value
            return datetime.date.fromisoformat(value)

        return to_date


class DateTime(sqltypes.DATETIME):
    def bind_processor(self, dialect):
        return super().bind_processor(dialect)

    def result_processor(self, dialect, coltype):
        def datetime_fmt(v):
            formats = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f")
            for fmt in formats:
                try:
                    time.strptime(v, fmt)
                except ValueError:
                    continue
                return fmt
            raise ValueError("Unknown date/time format")

        def to_datetime(v):
            if not isinstance(v, str):
                return v
            fmt = datetime_fmt(v)
            timestamp = time.strptime(v, fmt)
            return datetime.datetime.fromtimestamp(time.mktime(timestamp))

        return to_datetime


class EXADialect_websocket(EXADialect):
    driver = "exasol.driver.websocket.dbapi2"
    supports_statement_cache = False
    colspecs = {
        sqltypes.Integer: Integer,
        sqltypes.Numeric: Decimal,
        sqltypes.Date: Date,
        sqltypes.DateTime: DateTime,
    }

    @classmethod
    def dbapi(cls):
        return __import__(
            "exasol.driver.websocket.dbapi2", fromlist="exasol.driver.websocket"
        )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_connect_args(self, url):
        Converter = namedtuple("Converter", ["name", "map"])
        args, kwargs = [], url.translate_connect_args(database="schema")

        def tls(value):
            return True if not value == "SSL_VERIFY_NONE" else False

        def autocommit(value):
            value = value.lower()
            mapping = defaultdict(
                bool, {"y": True, "yes": "True", "n": False, "no": False}
            )
            return mapping[value]

        converters = {
            "SSLCertificate": Converter("tls", tls),
            "AUTOCOMMIT": Converter("autocommit", autocommit),
        }

        known_options = {
            option: value for option, value in url.query.items() if option in converters
        }
        for name, value in known_options.items():
            converter = converters[name]
            kwargs[converter.name] = converter.map(value)

        kwargs["dsn"] = f'{kwargs.pop("host")}:{kwargs.pop("port")}'

        return args, kwargs


dialect = EXADialect_websocket
