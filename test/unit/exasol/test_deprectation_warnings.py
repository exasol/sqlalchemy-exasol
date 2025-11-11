import pytest

from sqlalchemy_exasol.pyodbc import EXADialect_pyodbc


@pytest.mark.parametrize("klass,kwargs", [(EXADialect_pyodbc, {})])
def test_deprecation_warnings(klass, kwargs):
    with pytest.deprecated_call():
        EXADialect_pyodbc(**kwargs)
