"""
Connect string::

    exa+pyodbc://<username>:<password>@<dsnname>
    exa+pyodbc://<username>:<password>@<ip_range>:<port>/<schema>?<options>

"""

from exa.base import EXADialect, EXAExecutionContext
from sqlalchemy.connectors.pyodbc import PyODBCConnector
from sqlalchemy.util.langhelpers import asbool
from string import uppercase


class EXADialect_pyodbc(PyODBCConnector, EXADialect):

    execution_ctx_cls = EXAExecutionContext

    pyodbc_driver_name = "EXAODBC"

    server_version_info = None

    def __init__(self, **kw):
        # deal with http://code.google.com/p/pyodbc/issues/detail?id=25
        kw.setdefault('convert_unicode', True)
        super(EXADialect_pyodbc, self).__init__(**kw)

    def _get_server_version_info(self, connection):
        #TODO: need to check if current version of EXASOL returns proper server version
        # string on ODBC call
        if self.server_version_info is None:
            query = ("select DBMS_VERSION from EXA_STATISTICS.EXA_SYSTEM_EVENTS "
                 "where EVENT_TYPE='STARTUP' order by MEASURE_TIME desc "
                 "limit 1")
            result = connection.execute(query).fetchone()[0].split('.')
            self.server_version_info = (int(result[0]), int(result[1]), int(result[2]))
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
                connect_args[uppercase(param)] = asbool(keys.pop(param))

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

        connectors.extend(['%s=%s' % (k, v) for k, v in keys.iteritems()])
        return [[";".join(connectors)], connect_args]

dialect = EXADialect_pyodbc
