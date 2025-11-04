import hashlib
import random
import ssl

import pytest
import sqlalchemy.exc
from sqlalchemy import (
    create_engine,
    sql,
    testing,
)
from sqlalchemy.testing.fixtures import (
    TestBase,
    config,
)

FINGERPRINT_SECURITY_RATIONALE = (
    "Only websocket supports giving a fingerprint in the connection"
)


def get_fingerprint(dsn):
    import websocket

    ws = websocket.create_connection(
        f"wss://{dsn}", sslopt={"cert_reqs": ssl.CERT_NONE}
    )
    cert = ws.sock.getpeercert(True)
    ws.close()
    return hashlib.sha256(cert).hexdigest().upper()


def get_different_random_digit(value) -> str:
    choices = list(range(10))
    if value.isdigit():
        value = int(value)
        choices = [x for x in choices if x != value]

    return str(random.choice(choices))


class CertificateTest(TestBase):
    @staticmethod
    def perform_test_query(engine):
        query = "select 42 from dual"
        with engine.connect() as con:
            result = con.execute(sql.text(query)).fetchall()
        return result

    @staticmethod
    def remove_ssl_settings(url):
        """Create an equivalent url without the ssl/tls settings."""
        # Note:
        # This implementation is not backwards compatible with SQLA < 1.4, if you are looking for a
        # backwards compatible solution see:
        # * https://docs.sqlalchemy.org/en/14/changelog/migration_14.html#the-url-object-is-now-immutable
        query = dict(url.query)
        try:
            del query["SSLCertificate"]
        except KeyError:
            # nothing to do
            pass
        return url.set(query=query)

    @pytest.mark.skipif(
        testing.db.dialect.server_version_info < (7, 1, 0),
        reason="DB version(s) before 7.1.0 don't enforce ssl/tls",
    )
    def test_db_connection_fails_with_default_settings_for_self_signed_certificates(
        self,
    ):
        url = self.remove_ssl_settings(config.db.url)

        engine = create_engine(url)
        with pytest.raises(sqlalchemy.exc.DBAPIError) as exec_info:
            # we expect connect call to fail, but want to close it in case it succeeds
            with engine.connect():
                pass

        actual_message = f"{exec_info.value}"
        expected_substrings = ["self-signed certificate", "self signed certificate"]
        assert any([e in actual_message for e in expected_substrings])

    @pytest.mark.skipif(
        "websocket" not in testing.db.dialect.driver,
        reason="Only websocket supports passing on connect_args like this.",
    )
    def test_db_skip_certification_validation_passes(self):
        url = self.remove_ssl_settings(config.db.url)

        engine = create_engine(url, connect_args={"certificate_validation": False})
        result = self.perform_test_query(engine)
        assert result == [(42,)]

    def test_db_with_ssl_verify_none_passes(self):
        url = config.db.url
        query = dict(url.query)
        assert query.get("SSLCertificate") == "SSL_VERIFY_NONE"

        engine = create_engine(url)
        result = self.perform_test_query(engine)
        assert result == [(42,)]

    @pytest.mark.skipif(
        "websocket" not in testing.db.dialect.driver,
        reason=FINGERPRINT_SECURITY_RATIONALE,
    )
    def test_db_with_fingerprint_passes(self):
        url = self.remove_ssl_settings(config.db.url)
        connect_args = url.translate_connect_args(database="schema")
        fingerprint = get_fingerprint(f"{connect_args['host']}:{connect_args['port']}")

        query = dict(url.query)
        query["FINGERPRINT"] = fingerprint
        url = url.set(query=query)

        engine = create_engine(url)
        result = self.perform_test_query(engine)
        assert result == [(42,)]

    @pytest.mark.skipif(
        "websocket" not in testing.db.dialect.driver,
        reason=FINGERPRINT_SECURITY_RATIONALE,
    )
    def test_db_with_wrong_fingerprint_fails(self):
        url = self.remove_ssl_settings(config.db.url)
        connect_args = url.translate_connect_args(database="schema")
        fingerprint = get_fingerprint(f"{connect_args['host']}:{connect_args['port']}")

        query = dict(url.query)
        wrong_fingerprint = fingerprint[:-1] + get_different_random_digit(
            fingerprint[-1]
        )
        query["FINGERPRINT"] = wrong_fingerprint
        url = url.set(query=query)

        engine = create_engine(url)
        with pytest.raises(
            sqlalchemy.exc.DBAPIError,
            match=r"Provided fingerprint \[([A-F0-9]{64})\] did not match server fingerprint",
        ):
            self.perform_test_query(engine)
