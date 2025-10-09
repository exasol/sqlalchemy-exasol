import copy

import pytest
import sqlalchemy.exc
from sqlalchemy import (
    create_engine,
    testing,
)
from sqlalchemy.testing.fixtures import (
    TestBase,
    config,
)


class CertificateTest(TestBase):
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

        engine = create_engine(url, future=True)
        with pytest.raises(sqlalchemy.exc.DBAPIError) as exec_info:
            # we expect connect call to fail, but want to close it in case it succeeds
            with engine.connect():
                pass

        actual_message = f"{exec_info.value}"
        expected_substrings = ["self-signed certificate", "self signed certificate"]
        assert any([e in actual_message for e in expected_substrings])
