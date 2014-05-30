from sqlalchemy.dialects import registry

registry.register("exa.pyodbc", "sqlalchemy_exasol.pyodbc", "EXADialect_pyodbc")

from sqlalchemy.testing.plugin.pytestplugin import *
