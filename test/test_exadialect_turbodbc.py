from sqlalchemy import testing
from sqlalchemy.engine import url as sa_url
from sqlalchemy.testing import fixtures
from sqlalchemy.testing import eq_

from sqlalchemy_exasol.turbodbc import EXADialect_turbodbc, DEFAULT_CONNECTION_PARAMS


class EXADialectTurbodbcTest(fixtures.TestBase):
    __skip_if__ = (lambda: testing.db.dialect.driver != 'turbodbc',)

    dialect = None
    default_host_args = {
        'EXAHOST': '192.168.1.2..8:1234',
        'EXASCHEMA': 'my_schema'
    }
    default_user_args = {
        'UID': 'scott',
        'PWD': 'tiger',
    }

    def setup(self):
        self.dialect = EXADialect_turbodbc()

    def assert_parsed(self, dsn, expected_connector, expected_args):
        url = sa_url.make_url(dsn)
        connector, args = self.dialect.create_connect_args(url)
        eq_(connector, expected_connector)
        eq_(args, expected_args)

    def test_create_connect_args(self):
        expected = self.default_host_args.copy()
        expected.update(self.default_user_args)
        expected.update(DEFAULT_CONNECTION_PARAMS)
        self.assert_parsed("exa+turbodbc://scott:tiger@192.168.1.2..8:1234/my_schema", [None], expected)

    def test_create_connect_args_with_driver(self):
        expected = self.default_host_args.copy()
        expected.update(self.default_user_args)
        expected.update(DEFAULT_CONNECTION_PARAMS)
        expected['driver'] = 'EXASolo'
        self.assert_parsed(
            "exa+turbodbc://scott:tiger@192.168.1.2..8:1234/my_schema?driver=EXASolo",
            [None], expected)

    def test_create_connect_args_dsn(self):
        expected = self.default_user_args.copy()
        expected.update(DEFAULT_CONNECTION_PARAMS)
        self.assert_parsed("exa+pyodbc://scott:tiger@exa_test", ['exa_test'], expected)

    def test_create_connect_args_dsn_without_user(self):
        self.assert_parsed("exa+pyodbc://exa_test", ['exa_test'],
                           DEFAULT_CONNECTION_PARAMS)

    def test_create_connect_args_trusted(self):
        expected = self.default_host_args.copy()
        expected.update(DEFAULT_CONNECTION_PARAMS)
        self.assert_parsed("exa+pyodbc://192.168.1.2..8:1234/my_schema", [None], expected)

    def test_create_connect_args_with_param(self):
        expected = self.default_host_args.copy()
        expected.update(self.default_user_args)
        expected.update(DEFAULT_CONNECTION_PARAMS)
        expected['autocommit'] = 'true'
        self.assert_parsed("exa+pyodbc://scott:tiger@192.168.1.2..8:1234/my_schema?AUTOCOMMIT=true",
                           [None], expected)

    def test_create_connect_args_default_turbodbc_buffer(self):
        expected = self.default_host_args.copy()
        expected.update(self.default_user_args)
        expected.update(DEFAULT_CONNECTION_PARAMS)
        expected['rows_to_buffer'] = None
        self.assert_parsed(
            "exa+turbodbc://scott:tiger@192.168.1.2..8:1234/my_schema?rows_to_buffer=None",
            [None], expected)

    def test_create_connect_args_with_param_multiple(self):
        expected = self.default_host_args.copy()
        expected.update(self.default_user_args)
        expected.update(DEFAULT_CONNECTION_PARAMS)
        expected['rows_to_buffer'] = None
        expected['driver'] = 'EXADBDRIVER'
        expected['autocommit'] = 'true'
        self.assert_parsed(
            "exa+pyodbc://scott:tiger@192.168.1.2..8:1234/my_schema?autocommit=true&rows_to_buffer=None&driver=EXADBDRIVER",
            [None], expected)
