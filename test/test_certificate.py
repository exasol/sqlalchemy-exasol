import copy
import pytest
import sqlalchemy.exc
from sqlalchemy import create_engine
from sqlalchemy.testing.fixtures import config, TestBase


class CertificateTest(TestBase):
    def test_db_connection_fails_with_default_settings_for_self_signed_certificates(
        self,
    ):
        url = copy.deepcopy(config.db.url)
        if "SSLCertificate" in url.query:
            del url.query["SSLCertificate"]

        engine = create_engine(url)
        with pytest.raises(sqlalchemy.exc.DBAPIError) as exec_info:
            # we expect the connect call to fail, but want to close it in case it succeeds
            with engine.connect() as conn:
                pass

        assert "self signed certificate" in f"{exec_info.value}"
