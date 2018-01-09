import pyodbc

from mock import Mock

from sqlalchemy.engine import url as sa_url

from sqlalchemy.pool import _ConnectionFairy

from sqlalchemy import testing
from sqlalchemy.testing import fixtures
from sqlalchemy.testing import eq_

from sqlalchemy_exasol.pyodbc import EXADialect_pyodbc


class EXADialect_pyodbcTest(fixtures.TestBase):
    __skip_if__ = (lambda: testing.db.dialect.driver != 'pyodbc',)

    def setup(self):
        self.dialect = EXADialect_pyodbc()
        self.dialect.dbapi = pyodbc

    def assert_parsed(self, dsn, expected_connector, expected_args):
        url = sa_url.make_url(dsn)
        connector, args = self.dialect.create_connect_args(url)
        eq_(connector, expected_connector)
        eq_(args, expected_args)


    def test_create_connect_args(self):
        self.assert_parsed("exa+pyodbc://scott:tiger@192.168.1.2..8:1234/my_schema?driver=EXAODBC",
                 ['DRIVER={EXAODBC};EXAHOST=192.168.1.2..8:1234;EXASCHEMA=my_schema;UID=scott;PWD=tiger;INTTYPESINRESULTSIFPOSSIBLE=y'],
                 {})

    def test_create_connect_args_with_driver(self):
        self.assert_parsed("exa+pyodbc://scott:tiger@192.168.1.2..8:1234/my_schema?driver=FOOBAR",
                 ['DRIVER={FOOBAR};EXAHOST=192.168.1.2..8:1234;EXASCHEMA=my_schema;UID=scott;PWD=tiger;INTTYPESINRESULTSIFPOSSIBLE=y'],
                 {})

    def test_create_connect_args_dsn(self):
        self.assert_parsed("exa+pyodbc://scott:tiger@exa_test",
                 ['DSN=exa_test;EXAHOST=;EXASCHEMA=;UID=scott;PWD=tiger;INTTYPESINRESULTSIFPOSSIBLE=y'],
                 {})

    def test_create_connect_args_trusted(self):
        self.assert_parsed("exa+pyodbc://192.168.1.2..8:1234/my_schema",
                 ['DRIVER={None};EXAHOST=192.168.1.2..8:1234;EXASCHEMA=my_schema;Trusted_Connection=Yes;INTTYPESINRESULTSIFPOSSIBLE=y'],
                 {})


    def test_create_connect_args_autotranslate(self):
        self.assert_parsed("exa+pyodbc://scott:tiger@192.168.1.2..8:1234/my_schema?odbc_autotranslate=Yes",
                 ['DRIVER={None};EXAHOST=192.168.1.2..8:1234;EXASCHEMA=my_schema;UID=scott;PWD=tiger;AutoTranslate=Yes;INTTYPESINRESULTSIFPOSSIBLE=y'],
                 {})


    def test_create_connect_args_with_param(self):
        self.assert_parsed("exa+pyodbc://scott:tiger@192.168.1.2..8:1234/my_schema?autocommit=true",
                 ['DRIVER={None};EXAHOST=192.168.1.2..8:1234;EXASCHEMA=my_schema;UID=scott;PWD=tiger;INTTYPESINRESULTSIFPOSSIBLE=y'],
                 {'AUTOCOMMIT': True})


    def test_create_connect_args_with_param_multiple(self):
        self.assert_parsed("exa+pyodbc://scott:tiger@192.168.1.2..8:1234/my_schema?autocommit=true&ansi=false&unicode_results=false",
                 ['DRIVER={None};EXAHOST=192.168.1.2..8:1234;EXASCHEMA=my_schema;UID=scott;PWD=tiger;INTTYPESINRESULTSIFPOSSIBLE=y'],
                 {'AUTOCOMMIT': True, 'ANSI': False, 'UNICODE_RESULTS': False})


    def test_create_connect_args_with_unknown_params(self):
        self.assert_parsed("exa+pyodbc://scott:tiger@192.168.1.2..8:1234/my_schema?clientname=test&querytimeout=10",
                 ['DRIVER={None};EXAHOST=192.168.1.2..8:1234;EXASCHEMA=my_schema;UID=scott;PWD=tiger;INTTYPESINRESULTSIFPOSSIBLE=y;clientname=test;querytimeout=10'],
                 {})

    def test_is_disconnect(self):
        connection = Mock(spec=_ConnectionFairy)
        cursor = Mock(spec=pyodbc.Cursor)

        errors = [
            pyodbc.Error(
                'HY000',
                '[HY000] [EXASOL][EXASolution driver]Connection lost in socket read attempt. Operation timed out (-1) (SQLExecDirectW)'
            ),
            pyodbc.Error(
                'HY000',
                '[HY000] [EXASOL][EXASolution driver]Socket closed by peer.'
            ),
        ]

        for error in errors:
            status = self.dialect.is_disconnect(error, connection, cursor)

            eq_(status, True)
