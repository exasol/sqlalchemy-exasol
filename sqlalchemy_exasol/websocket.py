import datetime
import decimal
import time
from collections import (
    ChainMap,
    defaultdict,
    namedtuple,
)

from sqlalchemy.exc import ArgumentError
from sqlalchemy.sql import sqltypes

from sqlalchemy_exasol.base import EXADialect
from sqlalchemy_exasol.version import VERSION


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
            return lambda value: None if value is None else float(value)

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
            value = value.lower()
            mapping = defaultdict(
                lambda: True, {"y": True, "yes": "True", "n": False, "no": False}
            )
            return mapping[value]

        def certificate_validation(value):
            return True if value != "SSL_VERIFY_NONE" else False

        def autocommit(value):
            value = value.lower()
            mapping = defaultdict(
                bool, {"y": True, "yes": "True", "n": False, "no": False}
            )
            return mapping[value]

        converters = {
            "ENCRYPTION": Converter("tls", tls),
            "SSLCertificate": Converter(
                "certificate_validation", certificate_validation
            ),
            "AUTOCOMMIT": Converter("autocommit", autocommit),
        }
        defaults = {
            "tls": True,
            "certificate_validation": True,
            "client_name": "EXASOL:SQLA:WS",
            "client_version": VERSION,
        }
        known_options = {
            option: value for option, value in url.query.items() if option in converters
        }
        user_settings = {
            converters[name].name: converters[name].map(value)
            for name, value in known_options.items()
        }

        fingerprint = url.query.get("FINGERPRINT", None)
        if fingerprint:
            kwargs["dsn"] = f'{kwargs.pop("host")}/{fingerprint}:{kwargs.pop("port")}'
            user_settings["certificate_validation"] = False
        else:
            kwargs["dsn"] = f'{kwargs.pop("host")}:{kwargs.pop("port")}'

        kwargs = dict(**ChainMap(user_settings, kwargs, defaults))

        if not kwargs["tls"] and kwargs["certificate_validation"]:
            raise ArgumentError(
                "Certificate validation (True), can't be used without TLS (False)."
            )
        return args, kwargs


dialect = EXADialect_websocket
