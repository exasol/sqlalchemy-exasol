import os
import sys
from argparse import ArgumentParser
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

PROJECT_ROOT = Path(__file__).parent
# scripts path also contains administrative code/modules which are used by some nox targets
SCRIPTS = PROJECT_ROOT / "scripts"
sys.path.append(f"{SCRIPTS}")

from typing import (
    Iterable,
    Iterator,
    MutableMapping,
)

import nox
from git import tags
from links import check as _check
from links import documentation as _documentation
from links import urls as _urls
from nox import Session
from nox.sessions import SessionRunner
from pyodbc import (
    Connection,
    connect,
)
from version_check import (
    version_from_poetry,
    version_from_python_module,
    version_from_string,
)


class Settings:
    ITDE = PROJECT_ROOT / ".." / "integration-test-docker-environment"
    ODBC_DRIVER = PROJECT_ROOT / "driver" / "libexaodbc-uo2214lv2.so"
    CONNECTORS = ("pyodbc", "turbodbc")
    ENVIRONMENT_NAME = "test"
    DB_PORT = 8888
    BUCKETFS_PORT = 6666
    VERSION_FILE = PROJECT_ROOT / "sqlalchemy_exasol" / "version.py"
    DB_VERSIONS = ("7.1.9", "7.0.18")


# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = [
    f"verify(connector='{Settings.CONNECTORS[0]}', db_version='{Settings.DB_VERSIONS[0]}')"
]

ODBCINST_INI_TEMPLATE = dedent(
    """
    [ODBC]
    #Trace = yes
    #TraceFile =~/odbc.trace

    [EXAODBC]
    #Driver location will be appended in build environment:
    DRIVER={driver}

    """
)


def find_session_runner(session: Session, name: str) -> SessionRunner:
    """Helper function to find parameterized action by name"""
    for s, _ in session._runner.manifest.list_all_sessions():
        if name in s.signatures:
            return s
    session.error(f"Could not find a nox session by the name {name!r}")


def transaction(connection: Connection, sql_statements: Iterable[str]) -> None:
    cur = connection.cursor()
    for statement in sql_statements:
        cur.execute(statement)
    cur.commit()
    cur.close()


@contextmanager
def environment(env_vars: dict[str, str]) -> Iterator[MutableMapping[str, str]]:
    _env = os.environ.copy()
    os.environ.update(env_vars)
    yield os.environ
    os.environ.clear()
    os.environ.update(_env)


@contextmanager
def temporary_odbc_config(config: str) -> Iterator[Path]:
    with TemporaryDirectory() as tmp_dir:
        config_dir = Path(tmp_dir) / "odbcconfig"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "odbcinst.ini"
        with open(config_file, "w") as f:
            f.write(config)
        yield config_file


@contextmanager
def odbcconfig() -> Iterator[tuple[Path, MutableMapping[str, str]]]:
    with temporary_odbc_config(
        ODBCINST_INI_TEMPLATE.format(driver=Settings.ODBC_DRIVER)
    ) as cfg:
        env_vars = {"ODBCSYSINI": f"{cfg.parent.resolve()}"}
        with environment(env_vars) as env:
            yield cfg, env


def _python_files(path: Path) -> Iterator[Path]:
    files = filter(lambda path: "dist" not in path.parts, PROJECT_ROOT.glob("**/*.py"))
    files = filter(lambda path: ".eggs" not in path.parts, files)
    files = filter(lambda path: "venv" not in path.parts, files)
    return files


@nox.session(python=False)
def fix(session: Session) -> None:
    session.run(
        "poetry",
        "run",
        "python",
        f"{SCRIPTS / 'version_check.py'}",
        "--fix",
        f"{Settings.VERSION_FILE}",
    )
    files = [f"{path}" for path in _python_files(PROJECT_ROOT)]
    session.run(
        "poetry",
        "run",
        "python",
        "-m",
        "pyupgrade",
        "--py38-plus",
        "--exit-zero-even-if-changed",
        *files,
    )
    session.run("poetry", "run", "python", "-m", "isort", "-v", f"{PROJECT_ROOT}")
    session.run("poetry", "run", "python", "-m", "black", f"{PROJECT_ROOT}")


@nox.session(python=False)
def pyupgrade(session: Session) -> None:
    files = [f"{path}" for path in _python_files(PROJECT_ROOT)]
    session.run("poetry", "run", "python", "-m", "pyupgrade", "--py38-plus", *files)


@nox.session(name="code-format", python=False)
def code_format(session: Session) -> None:
    session.run(
        "poetry",
        "run",
        "python",
        "-m",
        "black",
        "--check",
        "--diff",
        "--color",
        f"{PROJECT_ROOT}",
    )


@nox.session(python=False)
def isort(session: Session) -> None:
    session.run(
        "poetry", "run", "python", "-m", "isort", "-v", "--check", f"{PROJECT_ROOT}"
    )


@nox.session(python=False)
def lint(session: Session) -> None:
    session.run(
        "poetry",
        "run",
        "python",
        "-m",
        "pylint",
        f'{PROJECT_ROOT / "scripts"}',
        f'{PROJECT_ROOT / "sqlalchemy_exasol"}',
    )


@nox.session(name="type-check", python=False)
def type_check(session: Session) -> None:
    session.run(
        "poetry",
        "run",
        "mypy",
        "--strict",
        "--show-error-codes",
        "--pretty",
        "--show-column-numbers",
        "--show-error-context",
        "--scripts-are-modules",
    )


@nox.session(python=False)
@nox.parametrize("db_version", Settings.DB_VERSIONS)
@nox.parametrize("connector", Settings.CONNECTORS)
def verify(session: Session, connector: str, db_version: str) -> None:
    """Prepare and run all available tests"""

    def is_version_in_sync() -> bool:
        return (
            version_from_python_module(Settings.VERSION_FILE) == version_from_poetry()
        )

    if not is_version_in_sync():
        session.error(
            "Versions out of sync, version file:"
            f"{version_from_python_module(Settings.VERSION_FILE)},"
            f"poetry: {version_from_poetry()}."
        )
    session.notify("isort")
    session.notify("pyupgrade")
    session.notify("code-format")
    session.notify("type-check")
    session.notify("lint")
    session.notify("type-check")
    session.notify(find_session_runner(session, f"db-start(db_version='{db_version}')"))
    session.notify(
        find_session_runner(session, f"integration(connector='{connector}')")
    )
    session.notify(find_session_runner(session, "db-stop"))


@nox.session(name="db-start", python=False)
@nox.parametrize("db_version", Settings.DB_VERSIONS)
def start_db(session: Session, db_version: str = Settings.DB_VERSIONS[0]) -> None:
    """Start the test database"""

    def start() -> None:
        # Consider adding ITDE as dev dependency once ITDE is packaged properly
        with session.chdir(Settings.ITDE):
            session.run(
                "bash",
                "start-test-env",
                "spawn-test-environment",
                "--environment-name",
                f"{Settings.ENVIRONMENT_NAME}",
                "--database-port-forward",
                f"{Settings.DB_PORT}",
                "--bucketfs-port-forward",
                f"{Settings.BUCKETFS_PORT}",
                "--docker-db-image-version",
                db_version,
                "--db-mem-size",
                "4GB",
                external=True,
            )

    def populate() -> None:
        with odbcconfig():
            settings = {
                "driver": "EXAODBC",
                "server": "localhost:8888",
                "user": "sys",
                "password": "exasol",
                "ssl_certificate": "SSL_VERIFY_NONE",
            }
            connection = connect(
                ";".join(
                    [
                        "DRIVER={driver}",
                        "EXAHOST={server}",
                        "UID={user}",
                        "PWD={password}",
                        "SSLCertificate={ssl_certificate}",
                    ]
                ).format(**settings)
            )
            transaction(
                connection,
                (
                    "CREATE SCHEMA TEST_SCHEMA;",
                    "CREATE SCHEMA TEST_SCHEMA_2;",
                ),
            )
            connection.close()

    start()
    populate()


@nox.session(name="db-stop", python=False)
def stop_db(session: Session) -> None:
    """Stop the test database"""
    session.run("docker", "kill", "db_container_test", external=True)
    session.run("docker", "kill", "test_container_test", external=True)


@nox.session(python=False)
@nox.parametrize("connector", Settings.CONNECTORS)
def integration(session: Session, connector: str) -> None:
    """Run(s) the integration tests for a specific connector. Expects a test database to be available."""

    with odbcconfig() as (config, env):
        uri = "".join(
            [
                "exa+{connector}:",
                "//sys:exasol@localhost:{db_port}",
                "/TEST?CONNECTIONLCALL=en_US.UTF-8&DRIVER=EXAODBC&SSLCertificate=SSL_VERIFY_NONE",
            ]
        ).format(connector=connector, db_port=Settings.DB_PORT)
        session.run("pytest", "--dropfirst", "--dburi", uri, external=True, env=env)


@nox.session(name="report-skipped", python=False)
def report_skipped(session: Session) -> None:
    """
    Runs all tests for all supported connectors and creates a csv report of skipped tests for each connector.

    Attention: This task expects a running test database (db-start).
    """

    with TemporaryDirectory() as tmp_dir:
        for connector in Settings.CONNECTORS:
            report = Path(tmp_dir) / f"test-report{connector}.json"
            with odbcconfig() as (config, env):
                uri = "".join(
                    [
                        "exa+{connector}:",
                        "//sys:exasol@localhost:{db_port}",
                        "/TEST?CONNECTIONLCALL=en_US.UTF-8&DRIVER=EXAODBC&SSLCertificate=SSL_VERIFY_NONE",
                    ]
                ).format(connector=connector, db_port=Settings.DB_PORT)
                session.run(
                    "pytest",
                    "--dropfirst",
                    "--dburi",
                    uri,
                    "--json-report",
                    f"--json-report-file={report}",
                    external=True,
                    env=env,
                )

                session.run(
                    "python",
                    f"{SCRIPTS / 'report.py'}",
                    "-f",
                    "csv",
                    "--output",
                    f"skipped-tests-{connector}.csv",
                    f"{connector}",
                    f"{report}",
                )


@nox.session(name="check-links", python=False)
def check_links(session: Session) -> None:
    """Checks weather or not all links in the documentation can be accessed"""
    errors = []
    for path, url in _urls(_documentation(PROJECT_ROOT)):
        status, details = _check(url)
        if status != 200:
            errors.append((path, url, status, details))

    if errors:
        session.error(
            "\n"
            + "\n".join(f"Url: {e[1]}, File: {e[0]}, Error: {e[3]}" for e in errors)
        )


@nox.session(name="list-links", python=False)
def list_links(session: Session) -> None:
    """List all links within the documentation"""
    for path, url in _urls(_documentation(PROJECT_ROOT)):
        session.log(f"Url: {url}, File: {path}")


@nox.session(python=False)
def release(session: Session) -> None:
    def create_parser() -> ArgumentParser:
        p = ArgumentParser(
            "Release a pypi package",
            usage="nox -s release -- [-h] [-d]",
        )
        p.add_argument("-d", "--dry-run", action="store_true", help="just do a dry run")
        return p

    args = []
    parser = create_parser()
    cli_args = parser.parse_args(session.posargs)
    if cli_args.dry_run:
        args.append("--dry-run")

    version_file = version_from_python_module(Settings.VERSION_FILE)
    module_version = version_from_poetry()
    git_version = version_from_string(list(tags())[-1])

    if not (module_version == git_version == version_file):
        session.error(
            f"Versions out of sync, version file: {version_file}, poetry: {module_version}, tag: {git_version}."
        )

    session.run(
        "poetry",
        "build",
        external=True,
    )

    session.run(
        "poetry",
        "publish",
        *args,
        external=True,
    )
