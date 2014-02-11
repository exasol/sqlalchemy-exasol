from sqlalchemy.dialects import registry

registry.register("exa.pyodbc", "exa.pyodbc", "EXADialect_pyodbc")

from sqlalchemy.testing import runner

runner.main()
