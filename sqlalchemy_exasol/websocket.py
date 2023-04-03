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


class EXADialect_websocket(EXADialect):
    driver = "exasol.driver.websocket.dbapi2"
    supports_statement_cache = False
    colspecs = {
        sqltypes.Integer: Integer,
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
