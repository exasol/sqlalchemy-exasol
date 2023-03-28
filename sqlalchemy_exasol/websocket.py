from collections import (
    defaultdict,
    namedtuple,
)

from sqlalchemy_exasol.base import EXADialect


class EXADialect_websocket(EXADialect):
    driver = "exasol.driver.websocket"
    supports_statement_cache = False

    @classmethod
    def dbapi(cls):
        return __import__("exasol.driver.websocket", fromlist="exasol.driver")

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
