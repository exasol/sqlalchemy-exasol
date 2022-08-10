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

        def sqla_1_4_and_above(url):
            query = dict(url.query)
            try:
                del query["SSLCertificate"]
            except KeyError:
                # nothing to do
                pass
            return url.set(query=query)

        def sqla_1_3_and_below(url):
            try:
                del url.query["SSLCertificate"]
            except KeyError:
                # nothing to do
                pass
            return url

        # Note: keep patching the URL backwards compatible
        # see also: https://docs.sqlalchemy.org/en/14/changelog/migration_14.html#the-url-object-is-now-immutable
        action = (
            sqla_1_4_and_above
            if hasattr(url, "update_query_dict")
            else sqla_1_3_and_below
        )
        url = action(url)

        return url

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
            # we expect the connect call to fail, but want to close it in case it succeeds
            with engine.connect() as conn:
                pass

        assert "self signed certificate" in f"{exec_info.value}"
