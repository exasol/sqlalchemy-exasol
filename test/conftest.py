from sqlalchemy.dialects import registry
import pytest

registry.register("exa.pyodbc", "sqlalchemy_exasol.pyodbc", "EXADialect_pyodbc")
registry.register("exa.turbodbc", "sqlalchemy_exasol.turbodbc", "EXADialect_turbodbc")

# Suppress spurious warning from pytest
pytest.register_assert_rewrite("sqlalchemy.testing.assertions")

from sqlalchemy.testing.plugin.pytestplugin import *
