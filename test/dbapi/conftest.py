import os
from collections import ChainMap
from dataclasses import dataclass

import pytest


def _option_name(name: str):
    return f"--exasol-{name}"


def _envvar_name(name: str):
    return f"EXASOL_{name.upper()}"


_OPTIONS = ["port", "host", "username", "password", "schema"]

_DEFAULTS = {
    _envvar_name("port"): 8888,
    _envvar_name("host"): "localhost",
    _envvar_name("username"): "SYS",
    _envvar_name("password"): "exasol",
    _envvar_name("schema"): "TEST",
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


@dataclass
class Config:
    """Exasol integration test configuration"""

    host: str
    port: int
    username: str
    password: str
    schema: str


@pytest.fixture
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
