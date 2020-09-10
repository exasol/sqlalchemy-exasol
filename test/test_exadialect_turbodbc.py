from sqlalchemy import testing
from sqlalchemy.engine import url as sa_url
from sqlalchemy.testing import fixtures
from sqlalchemy.testing import eq_

from sqlalchemy_exasol.turbodbc import (EXADialect_turbodbc, DEFAULT_CONNECTION_PARAMS,
                                        DEFAULT_TURBODBC_PARAMS)


class EXADialectTurbodbcTest(fixtures.TestBase):
    __skip_if__ = (lambda: testing.db.dialect.driver != 'turbodbc',)

    dialect = None
    default_host_args = {
        'exahost': '192.168.1.2..8:1234',
        'exaschema': 'my_schema'
    }
    default_user_args = {
        'uid': 'scott',
        'pwd': 'tiger',
    }

    @staticmethod
    def _assert_connect_args(result, expected, expected_turbodbc):
        eq_({k: v for k,v in result.items() if k != 'turbodbc_options'}, expected)
        assert (result['turbodbc_options'].read_buffer_size.megabytes
                == expected_turbodbc.get('read_buffer_size', 50))
        assert (result['turbodbc_options'].parameter_sets_to_buffer
                == expected_turbodbc.get('parameter_sets_to_buffer', 1000))
        assert (result['turbodbc_options'].use_async_io
                == expected_turbodbc.get('use_async_io', False))

    def setup(self):
        self.dialect = EXADialect_turbodbc()

    def _get_connection_arguments(self, dsn):
        url = sa_url.make_url(dsn)
        _, args = self.dialect.create_connect_args(url)
        return args

    def assert_parsed(self, dsn, expected_connector, expected_args, expected_turbodbc_args):
        url = sa_url.make_url(dsn)
        connector, args = self.dialect.create_connect_args(url)
        eq_(connector, expected_connector)
        self._assert_connect_args(args, expected_args, expected_turbodbc_args)


    def test_create_connect_args(self):
        expected = self.default_host_args.copy()
        expected.update(self.default_user_args)
        expected.update(DEFAULT_CONNECTION_PARAMS)
        self.assert_parsed("exa+turbodbc://scott:tiger@192.168.1.2..8:1234/my_schema", [None],
                           expected, {})

    def test_create_connect_args_with_driver(self):
        expected = self.default_host_args.copy()
        expected.update(self.default_user_args)
        expected.update(DEFAULT_CONNECTION_PARAMS)
        expected['driver'] = 'EXASolo'
        self.assert_parsed(
            "exa+turbodbc://scott:tiger@192.168.1.2..8:1234/my_schema?driver=EXASolo",
            [None], expected, {})

    def test_create_connect_args_dsn_without_user(self):
        self.assert_parsed("exa+turbodbc://exa_test", ['exa_test'],
                           DEFAULT_CONNECTION_PARAMS, {})

    def test_create_connect_args_dsn(self):
        expected = self.default_user_args.copy()
        expected.update(DEFAULT_CONNECTION_PARAMS)
        self.assert_parsed("exa+pyodbc://scott:tiger@exa_test", ['exa_test'], expected, {})

    def test_create_connect_args_with_turbodbc_args(self):
        expected = self.default_host_args.copy()
        expected.update(self.default_user_args)
        expected.update(DEFAULT_CONNECTION_PARAMS)
        self.assert_parsed("exa+turbodbc://scott:tiger@192.168.1.2..8:1234/my_schema?"
                           "read_buffer_size=4200&parameter_sets_to_buffer=111&use_async_io=True"
                           "&varchar_max_character_limit=99&prefer_unicode=True"
                           "&large_decimals_as_64_bit_types=True"
                           "&limit_varchar_results_to_max=True"
                           "&autocommit=True",
                           [None], expected, {'read_buffer_size': 4200,
                                              'parameter_sets_to_buffer': 111,
                                              'use_async_io': True,
                                              'varchar_max_character_limit': 99,
                                              'prefer_unicode': True,
                                              'large_decimals_as_64_bit_types': True,
                                              'limit_varchar_results_to_max': True,
                                              'autocommit': True})

    def test_create_connect_args_trusted(self):
        expected = self.default_host_args.copy()
        expected.update(DEFAULT_CONNECTION_PARAMS)
        self.assert_parsed("exa+pyodbc://192.168.1.2..8:1234/my_schema", [None], expected, {})

    def test_create_connect_args_with_custom_parameter(self):
        base_url = "exa+pyodbc://scott:tiger@192.168.1.2..8:1234/my_schema"
        assert "custom" not in self._get_connection_arguments(base_url)
        assert self._get_connection_arguments(base_url + "?CUSTOM=something")["custom"] == 'something'

    def test_create_connect_args_with_parameter_set_to_none(self):
        base_url = "exa+pyodbc://scott:tiger@192.168.1.2..8:1234/my_schema"
        assert self._get_connection_arguments(base_url + "?CUSTOM=None")["custom"] is None

    def test_create_connect_args_overrides_default(self):
        base_url = "exa+pyodbc://scott:tiger@192.168.1.2..8:1234/my_schema"

        before = self._get_connection_arguments(base_url)["inttypesinresultsifpossible"]
        after = self._get_connection_arguments(base_url + "?inttypesinresultsifpossible=custom")["inttypesinresultsifpossible"]
        assert before != after
