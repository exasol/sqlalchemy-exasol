from sqlalchemy.dialects import registry

registry.register("exa.pyodbc", "sqlalchemy_exasol.pyodbc", "EXADialect_pyodbc")

from sqlalchemy.testing import runner

def run():
    runner.main()

if __name__ == '__main__':
    run()
