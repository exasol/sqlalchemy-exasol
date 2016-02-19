"""
Connect string::

    exa+pyodbc://<username>:<password>@<dsnname>
    exa+pyodbc://<username>:<password>@<ip_range>:<port>/<schema>?<options>

"""

import re
import six
from sqlalchemy_exasol.base import EXADialect, EXAExecutionContext
from sqlalchemy.connectors.pyodbc import PyODBCConnector
from sqlalchemy.util.langhelpers import asbool
from distutils.version import LooseVersion

class EXADialect_pyodbc(PyODBCConnector, EXADialect):

    execution_ctx_cls = EXAExecutionContext

    pyodbc_driver_name = "EXAODBC"
    driver_version = None
    server_version_info = None

    def __init__(self, **kw):
        # deal with http://code.google.com/p/pyodbc/issues/detail?id=25
        kw.setdefault('convert_unicode', True)
        super(EXADialect_pyodbc, self).__init__(**kw)

    def get_driver_version(self, connection):
        # LooseVersion will also work with interim versions like '4.2.7dev1' or '5.0.rc4'
        if self.driver_version is None:
            self.driver_version = LooseVersion( connection.connection.getinfo( self.dbapi.SQL_DRIVER_VER ) or '2.0.0' )
        return self.driver_version

    def _get_server_version_info(self, connection):
        if self.server_version_info is None:
            # need to check if current version of EXAODBC returns proper server version
            if self.get_driver_version(connection) >= LooseVersion('4.2.1'):
                # v4.2.1 and above should deliver usable SQL_DBMS_VER
                result = connection.connection.getinfo( self.dbapi.SQL_DBMS_VER ).split('.')
            else:
                # Older versions do not include patchlevels, so we need to get info through SQL call
                query = "select PARAM_VALUE from SYS.EXA_METADATA where PARAM_NAME = 'databaseProductVersion'"
                result = connection.execute(query).fetchone()[0].split('.')

            self.server_version_info = (int(result[0]), int(result[1]), int(result[2]))

        # return cached info
        return self.server_version_info

    def create_connect_args(self, url):
        """
        Connection strings are EXASolution specific. See EXASolution manual
        on Connection-String-Parameters
        """
        opts = url.translate_connect_args(username='user')
        opts.update(url.query)
        # always enable efficient conversion to Python types: see https://www.exasol.com/support/browse/EXASOL-898
        opts['INTTYPESINRESULTSIFPOSSIBLE'] = 'y'

        keys = opts
        query = url.query

        connect_args = {}
        for param in ('ansi', 'unicode_results', 'autocommit'):
            if param in keys:
                connect_args[param.upper()] = asbool(keys.pop(param))

        dsn_connection = 'dsn' in keys or \
                        ('host' in keys and 'port' not in keys)
        if dsn_connection:
            connectors = ['DSN=%s' % (keys.pop('host', '') or \
                        keys.pop('dsn', ''))]
        else:
            port = ''
            if 'port' in keys and not 'port' in query:
                port = ':%d' % int(keys.pop('port'))

            connectors = ["DRIVER={%s}" %
                            keys.pop('driver', self.pyodbc_driver_name),
                          'EXAHOST=%s%s' % (keys.pop('host', ''), port),
                          'EXASCHEMA=%s' % keys.pop('database', '')]

        user = keys.pop("user", None)
        if user:
            connectors.append("UID=%s" % user)
            connectors.append("PWD=%s" % keys.pop('password', ''))
        else:
            connectors.append("Trusted_Connection=Yes")

        # if set to 'Yes', the ODBC layer will try to automagically
        # convert textual data from your database encoding to your
        # client encoding.  This should obviously be set to 'No' if
        # you query a cp1253 encoded database from a latin1 client...
        if 'odbc_autotranslate' in keys:
            connectors.append("AutoTranslate=%s" %
                                keys.pop("odbc_autotranslate"))

        connectors.extend(['%s=%s' % (k, v) for k, v in sorted(six.iteritems(keys))])
        return [[";".join(connectors)], connect_args]

    def is_disconnect(self, e, connection, cursor):
        if isinstance(e, self.dbapi.Error):
            error_codes = {
                '40004', # Connection lost.
                '40009', # Connection lost after internal server error.
                '40018', # Connection lost after system running out of memory.
                '40020', # Connection lost after system running out of memory.
            }
            exasol_error_codes = {
                'HY000': (  # Generic Exasol error code
                    re.compile(ur'operation timed out', re.IGNORECASE),
                    re.compile(ur'connection lost', re.IGNORECASE),
                )
            }

            error_code, error_msg = e.args[:2]

            # import pdb; pdb.set_trace()
            if error_code in exasol_error_codes:
                # Check exasol error
                for msg_re in exasol_error_codes[error_code]:
                    if msg_re.search(error_msg):
                        return True

                return False

            # Check Pyodbc error
            return error_code in error_codes

        return super(EXADialect_pyodbc, self).is_disconnect(e, connection, cursor)

dialect = EXADialect_pyodbc
