from __future__ import annotations

import argparse
import sys
import webbrowser
from argparse import ArgumentParser
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).parent
# scripts path also contains administrative code/modules which are used by some nox targets
SCRIPTS = PROJECT_ROOT / "scripts"
DOC = PROJECT_ROOT / "doc"
DOC_BUILD = DOC / "build"
sys.path.append(f"{SCRIPTS}")

from typing import Iterator

import nox
from git_helpers import tags
from links import check as _check
from links import documentation as _documentation
from links import urls as _urls
from nox import Session
from nox.sessions import SessionRunner
from version_check import (
    version_from_poetry,
    version_from_python_module,
    version_from_string,
)

from exasol.driver.odbc import (
    ODBC_DRIVER,
    odbcconfig,
)

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["fix"]


class Settings:
    CONNECTORS = ("pyodbc", "turbodbc", "websocket")
    ENVIRONMENT_NAME = "test"
    DB_PORT = 8563
    BUCKETFS_PORT = 2580
    VERSION_FILE = PROJECT_ROOT / "sqlalchemy_exasol" / "version.py"
    DB_VERSIONS = ("7.1.17",)


def find_session_runner(session: Session, name: str) -> SessionRunner:
    """Helper function to find parameterized action by name"""
    for s, _ in session._runner.manifest.list_all_sessions():
        if name in s.signatures:
            return s
    session.error(f"Could not find a nox session by the name {name!r}")


def _python_files(path: Path) -> Iterator[Path]:
    files = filter(lambda path: "dist" not in path.parts, PROJECT_ROOT.glob("**/*.py"))
    files = filter(lambda path: ".eggs" not in path.parts, files)
    files = filter(lambda path: "venv" not in path.parts, files)
    return files


@nox.session(python=False)
def fix(session: Session) -> None:
    """Run all available formatters and code upgrade tools against the code base"""

    def apply_pyupgrade_fixes(session: Session) -> None:
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

    session.run(
        "poetry",
        "run",
        "python",
        f"{SCRIPTS / 'version_check.py'}",
        "--fix",
        f"{Settings.VERSION_FILE}",
    )
    apply_pyupgrade_fixes(session)
    session.run("poetry", "run", "python", "-m", "isort", "-v", f"{PROJECT_ROOT}")
    session.run("poetry", "run", "python", "-m", "black", f"{PROJECT_ROOT}")


@nox.session(python=False)
def check(session: Session) -> None:
    """Run all available source code checks against the code base (typecheck, linters, formatters, etc.)"""

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


@nox.session(name="db-start", python=False)
def start_db(session: Session) -> None:
    """Start a test database. For more details append '-- -h'"""

    def parser() -> ArgumentParser:
        p = ArgumentParser(
            usage="nox -s start-db -- [-h] [--db-version]",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        p.add_argument(
            "--db-version",
            choices=Settings.DB_VERSIONS,
            default=Settings.DB_VERSIONS[0],
            help="which will be used",
        )
        return p

    def start(db_version: str) -> None:
        session.run(
            "itde",
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

    args = parser().parse_args(session.posargs)
    start(args.db_version)


@nox.session(name="db-stop", python=False)
def stop_db(session: Session) -> None:
    """Stop the test database"""
    session.run("docker", "kill", "db_container_test", external=True)


@nox.session(name="sqla-tests", python=False)
def sqlalchemy_tests(session: Session) -> None:
    """
    Run the sqlalchemy integration tests suite. For more details append '-- -h'

    Attention:

        Make sure the sqla compliance suite is run in isolation, to avoid side effects from custom tests
        e.g. because of unintended implicit schema open/closes.

        Expects a running test db
    """

    def parser() -> ArgumentParser:
        p = ArgumentParser(
            usage="nox -s sqla-tests -- [-h] [--connector]",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        p.add_argument(
            "--connector",
            choices=Settings.CONNECTORS,
            default=Settings.CONNECTORS[0],
            help="which will be used",
        )
        return p

    with odbcconfig(ODBC_DRIVER) as (config, env):
        args = parser().parse_args(session.posargs)
        connector = args.connector
        session.run(
            "pytest",
            "--dropfirst",
            "--db",
            f"exasol-{connector}",
            f"{PROJECT_ROOT / 'test' / 'integration' / 'sqlalchemy'}",
            external=True,
            env=env,
        )


@nox.session(name="unit-tests", python=False)
def unit_tests(session: Session) -> None:
    """Run the unit tests"""
    session.run(
        "pytest",
        f"{PROJECT_ROOT / 'test' / 'unit'}",
        external=True,
    )


@nox.session(name="exasol-tests", python=False)
def exasol_tests(session: Session) -> None:
    """Run the integration tests with a specific connector. For more details append '-- -h'"""

    def parser() -> ArgumentParser:
        p = ArgumentParser(
            usage="nox -s exasol-tests -- [-h] [--connector]",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        p.add_argument(
            "--connector",
            choices=Settings.CONNECTORS,
            default=Settings.CONNECTORS[0],
            help="which will be used",
        )
        return p

    with odbcconfig(ODBC_DRIVER) as (config, env):
        args = parser().parse_args(session.posargs)
        connector = args.connector
        session.run(
            "pytest",
            "--dropfirst",
            "--db",
            f"exasol-{connector}",
            f"{PROJECT_ROOT / 'test' / 'integration' / 'exasol'}",
            external=True,
            env=env,
        )

    session.run("pytest", f"{PROJECT_ROOT / 'test' / 'integration' / 'dbapi'}")


@nox.session(name="regression-tests", python=False)
def regression_tests(session: Session) -> None:
    """Run regression tests"""
    session.run("pytest", f"{PROJECT_ROOT / 'test' / 'integration' / 'regression'}")


@nox.session(name="integration-tests", python=False)
def integration_tests(session: Session) -> None:
    """Run integration tests with a specific configuration. For more details append '-- -h'"""

    def parser() -> ArgumentParser:
        p = ArgumentParser(
            usage="nox -s integration-tests -- [-h] [--connector] [--db-version]",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        p.add_argument(
            "--connector",
            choices=Settings.CONNECTORS,
            default=Settings.CONNECTORS[0],
            help="which will be used",
        )
        p.add_argument(
            "--db-version",
            choices=Settings.DB_VERSIONS,
            default=Settings.DB_VERSIONS[0],
            help="which will be used",
        )
        return p

    args = parser().parse_args(session.posargs)
    session.notify(
        find_session_runner(session, "db-start"),
        posargs=["--db-version", f"{args.db_version}"],
    )
    session.notify(
        find_session_runner(session, f"sqla-tests"),
        posargs=["--connector", f"{args.connector}"],
    )
    session.notify(
        find_session_runner(session, f"exasol-tests"),
        posargs=["--connector", f"{args.connector}"],
    )
    session.notify(
        find_session_runner(session, f"regression-tests"),
    )
    session.notify(find_session_runner(session, "db-stop"))


@nox.session(python=False, name="clean-docs")
def clean(session: Session) -> None:
    """Remove all documentation artifacts"""
    if DOC_BUILD.exists():
        rmtree(DOC_BUILD.resolve())
        session.log(f"Removed {DOC_BUILD}")


@nox.session(python=False, name="build-docs")
def build(session: Session) -> None:
    """Build the documentation"""
    session.run(
        "poetry",
        "run",
        "sphinx-build",
        "-b",
        "html",
        "-W",
        f"{DOC}",
        f"{DOC_BUILD}",
        external=True,
    )


@nox.session(python=False, name="open-docs")
def open_docs(session: Session) -> None:
    """Open the documentation in the browser"""
    index_page = DOC_BUILD / "index.html"
    if not index_page.exists():
        session.error(
            f"File {index_page} does not exist." "Please run `nox -s build-docs` first"
        )

    webbrowser.open_new_tab(index_page.resolve().as_uri())


@nox.session(python=False)
def release(session: Session) -> None:
    """Release a sqlalchemy-exasol package. For more details append '-- -h'"""

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


@nox.session(python=False)
def pyupgrade(session: Session) -> None:
    """Run pyupgrade against the code base"""
    files = [f"{path}" for path in _python_files(PROJECT_ROOT)]
    session.run("poetry", "run", "python", "-m", "pyupgrade", "--py38-plus", *files)


@nox.session(name="code-format", python=False)
def code_format(session: Session) -> None:
    """Run the code formatter against the codebase"""
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
    """Run isort against the codebase"""
    session.run(
        "poetry", "run", "python", "-m", "isort", "-v", "--check", f"{PROJECT_ROOT}"
    )


@nox.session(python=False)
def lint(session: Session) -> None:
    """Run the linter against the codebase"""
    session.run(
        "poetry",
        "run",
        "python",
        "-m",
        "pylint",
        f'{PROJECT_ROOT / "exasol"}',
        f'{PROJECT_ROOT / "scripts"}',
        f'{PROJECT_ROOT / "sqlalchemy_exasol"}',
    )


@nox.session(name="type-check", python=False)
def type_check(session: Session) -> None:
    """Run the type checker against the codebase"""
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


@nox.session(name="report-skipped", python=False)
def report_skipped(session: Session) -> None:
    """
    Runs all tests for all supported connectors and creates a csv report of skipped tests for each connector.

    Attention: This task expects a running test database (db-start).
    """
    with TemporaryDirectory() as tmp_dir:
        for connector in Settings.CONNECTORS:
            report = Path(tmp_dir) / f"test-report{connector}.json"
            with odbcconfig(ODBC_DRIVER) as (config, env):
                session.run(
                    "pytest",
                    "--dropfirst",
                    "--db",
                    f"exasol-{connector}",
                    f"{PROJECT_ROOT / 'test' / 'integration' / 'sqlalchemy'}",
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
