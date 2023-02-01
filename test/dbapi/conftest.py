import os
from collections import ChainMap
from dataclasses import dataclass

import pyexasol
import pytest


def _option_name(name: str):
    return f"--exasol-{name}"


def _envvar_name(name: str):
    return f"EXASOL_{name.upper()}"


_OPTIONS = ["port", "host", "username", "password", "schema", "bootstrap"]

_DEFAULTS = {
    _envvar_name("port"): 8888,
    _envvar_name("host"): "localhost",
    _envvar_name("username"): "SYS",
    _envvar_name("password"): "exasol",
    _envvar_name("schema"): "TEST",
    _envvar_name("bootstrap"): False,
}


def pytest_addoption(parser):
    group = parser.getgroup("exasol")
    group.addoption(
        _option_name("port"),
        type=int,
        help="Port on which the exasol db is listening (default: 8888).",
    )
    group.addoption(
        _option_name("host"),
        type=str,
        help="Host to connect to (default: 'localhost').",
    )
    group.addoption(
        _option_name("username"),
        type=str,
        help="Username used to authenticate against the exasol db (default: 'SYS').",
    )
    group.addoption(
        _option_name("password"),
        type=str,
        help="Password used to authenticate against the exasol db (default: 'exasol').",
    )
    group.addoption(
        _option_name("schema"),
        type=str,
        help=f"Schema to open after connecting to the db (default: TEST).",
    )
    group.addoption(
        _option_name("bootstrap"),
        type=bool,
        help=f"Signals that pytest itself should start the exasol db rather than using an active one (default: False).",
    )


@dataclass
class Config:
    """Exasol integration test configuration"""

    host: str
    port: int
    username: str
    password: str
    schema: str
    bootstrap: bool


@pytest.fixture(scope="session")
def exasol_test_config(request) -> Config:
    """
    Provides configuration information of the test environment.

    This configuration complies with common cli conventions and takes the
    following configurations into account (precedence highest to lowest):
        * pytest cli arguments
        * ENVIRONMENT variables
        * default settings
    """
    env_to_option = {_envvar_name(o): o for o in _OPTIONS}
    env = {env_to_option[k]: v for k, v in os.environ.items() if k in _DEFAULTS and v}
    defaults = {env_to_option[k]: v for k, v in _DEFAULTS.items()}
    options = request.config.option
    pytest_options = {
        k: v
        for k, v in dict(
            host=options.exasol_host,
            port=options.exasol_port,
            username=options.exasol_username,
            password=options.exasol_password,
            schema=options.exasol_schema,
        ).items()
        if v
    }
    options = ChainMap(pytest_options, env, defaults)
    return Config(**options)


@pytest.fixture
def db_connection(exasol_test_config):
    """
    Returns a db connection which can be used to interact with the test database.
    """
    config = exasol_test_config
    connection = pyexasol.connect(
        dsn=f"{config.host}:{config.port}",
        user=config.username,
        password=config.password,
    )
    yield connection
    connection.close()


@pytest.fixture(scope="session")
def test_schema():
    yield "TEST"


@pytest.fixture(scope="session")
def exasol_db(exasol_test_config, test_schema):
    """
    Sets up an exasol db for testion.
    """
    config = exasol_test_config

    if config.bootstrap:
        raise Exception("Bootstrapping the db from pytest is not supported yet")

    connection = pyexasol.connect(
        dsn=f"{config.host}:{config.port}",
        user=config.username,
        password=config.password,
    )

    connection.execute(f"DROP SCHEMA IF EXISTS {test_schema} CASCADE;")
    connection.execute(f"CREATE SCHEMA {test_schema};")
    connection.commit()

    yield

    connection.execute(f"DROP SCHEMA IF EXISTS {test_schema} CASCADE;")
    connection.commit()
    connection.close()

    if config.bootstrap:
        # TODO: once the bootstrapping is implemented th shutdown code goes here
        pass
