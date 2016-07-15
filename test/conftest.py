from sqlalchemy.dialects import registry

registry.register("exa.pyodbc", "sqlalchemy_exasol.pyodbc", "EXADialect_pyodbc")
registry.register("exa.turbodbc", "sqlalchemy_exasol.turbodbc", "EXADialect_turbodbc")

from sqlalchemy.testing.plugin.pytestplugin import *
