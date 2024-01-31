import pytest
from sqlalchemy_exasol.pyodbc import EXADialect_pyodbc
from sqlalchemy_exasol.turbodbc import EXADialect_turbodbc


@pytest.mark.parametrize(
    "klass,kwargs",
    [
        (EXADialect_pyodbc, {}),
        (EXADialect_turbodbc, {})
    ]
)
def test_deprectation_warnings(klass, kwargs):
    with pytest.deprecated_call():
        _ = EXADialect_pyodbc(**kwargs)

