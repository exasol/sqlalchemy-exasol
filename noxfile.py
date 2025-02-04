from __future__ import annotations

import argparse
import sys
import webbrowser
from argparse import ArgumentParser
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryDirectory

# fmt: off
PROJECT_ROOT = Path(__file__).parent
# scripts path also contains administrative code/modules which are used by some nox targets
SCRIPTS = PROJECT_ROOT / "scripts"
DOC = PROJECT_ROOT / "doc"
DOC_BUILD = DOC / "build"
sys.path.append(f"{SCRIPTS}")
# fmt: on

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

from exasol.odbc import (
    ODBC_DRIVER,
    odbcconfig,
)

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["project:fix"]


from noxconfig import PROJECT_CONFIG


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


from exasol.toolbox.nox._format import (
    Mode,
    _code_format,
    _pyupgrade,
    _version,
    fix,
)


@nox.session(name="project:check", python=False)
def check(session: Session) -> None:
    """Runs all available checks on the project"""
    from exasol.toolbox.nox._lint import (
        _pylint,
        _type_check,
    )

    py_files = [f"{file}" for file in _python_files(PROJECT_CONFIG.root)]
    _version(session, Mode.Check, PROJECT_CONFIG.version_file)
    _code_format(session, Mode.Check, py_files)
    _pylint(session, py_files)
    _type_check(session, py_files)


from exasol.toolbox.nox._lint import (
    lint,
    type_check,
)
from exasol.toolbox.nox._metrics import report


@nox.session(name="db:start", python=False)
def start_db(session: Session) -> None:
    """Start a test database. For more details append '-- -h'"""

    def parser() -> ArgumentParser:
        p = ArgumentParser(
            usage="nox -s db:start -- [-h] [--db-version]",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        p.add_argument(
            "--db-version",
            choices=PROJECT_CONFIG.exasol_versions,
            default=PROJECT_CONFIG.exasol_versions[0],
            help="which will be used",
        )
        return p

    def start(db_version: str) -> None:
        session.run(
            "itde",
            "spawn-test-environment",
            "--environment-name",
            f"{PROJECT_CONFIG.environment_name}",
            "--database-port-forward",
            f"{PROJECT_CONFIG.db_port}",
            "--bucketfs-port-forward",
            f"{PROJECT_CONFIG.bucketfs_port}",
            "--docker-db-image-version",
            db_version,
            "--db-mem-size",
            "4GB",
            external=True,
        )

    args = parser().parse_args(session.posargs)
    start(args.db_version)


@nox.session(name="db:stop", python=False)
def stop_db(session: Session) -> None:
    """Stop the test database"""
    session.run("docker", "kill", "db_container_test", external=True)


def _coverage_command():
    coverage_command = [
        "coverage",
        "run",
        "-a",
        f"--rcfile={PROJECT_ROOT / 'pyproject.toml'}",
        "-m",
    ]
    return coverage_command


@nox.session(name="test:sqla", python=False)
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
            usage="nox -s test:sqla -- [-h] [--connector]",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        p.add_argument(
            "--connector",
            choices=PROJECT_CONFIG.connectors,
            default=PROJECT_CONFIG.connectors[0],
            help="which will be used",
        )
        return p

    with odbcconfig(ODBC_DRIVER) as (config, env):
        args = parser().parse_args(session.posargs)
        connector = args.connector
        session.run(
            *_coverage_command(),
            "pytest",
            "--dropfirst",
            "--db",
            f"exasol-{connector}",
            f"{PROJECT_ROOT / 'test' / 'integration' / 'sqlalchemy'}",
            external=True,
            env=env,
        )


@nox.session(name="test:unit", python=False)
def unit_tests(session: Session) -> None:
    """Run the unit tests"""
    session.run(
        "pytest",
        f"{PROJECT_ROOT / 'test' / 'unit'}",
        external=True,
    )


@nox.session(name="test:exasol", python=False)
def exasol_tests(session: Session) -> None:
    """Run the integration tests with a specific connector. For more details append '-- -h'"""

    def parser() -> ArgumentParser:
        p = ArgumentParser(
            usage="nox -s test:exasol -- [-h] [--connector]",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        p.add_argument(
            "--connector",
            choices=PROJECT_CONFIG.connectors,
            default=PROJECT_CONFIG.connectors[0],
            help="which will be used",
        )
        return p

    with odbcconfig(ODBC_DRIVER) as (config, env):
        args = parser().parse_args(session.posargs)
        connector = args.connector
        session.run(
            *_coverage_command(),
            "pytest",
            "--dropfirst",
            "--db",
            f"exasol-{connector}",
            f"{PROJECT_ROOT / 'test' / 'integration' / 'exasol'}",
            external=True,
            env=env,
        )


@nox.session(name="test:regression", python=False)
def regression_tests(session: Session) -> None:
    """Run regression tests"""
    session.run(
        *_coverage_command(),
        "pytest",
        f"{PROJECT_ROOT / 'test' / 'integration' / 'regression'}",
    )


@nox.session(name="test:integration", python=False)
def integration_tests(session: Session) -> None:
    """Run integration tests with a specific configuration. For more details append '-- -h'"""

    def parser() -> ArgumentParser:
        p = ArgumentParser(
            usage="nox -s test:integration -- [-h] [--connector] [--db-version]",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        p.add_argument(
            "--connector",
            choices=PROJECT_CONFIG.connectors,
            default=PROJECT_CONFIG.connectors[0],
            help="which will be used",
        )
        p.add_argument(
            "--db-version",
            choices=PROJECT_CONFIG.exasol_versions,
            default=PROJECT_CONFIG.exasol_versions[0],
            help="which will be used",
        )
        p.add_argument(
            "--coverage",
            action="store_true",
            help="This is only here for compatibility. Coverage will always be collected.",
        )
        return p

    coverage_file = PROJECT_ROOT / ".coverage"
    coverage_file.unlink(missing_ok=True)

    args = parser().parse_args(session.posargs)
    session.notify(
        find_session_runner(session, "db:start"),
        posargs=["--db-version", f"{args.db_version}"],
    )
    session.notify(
        find_session_runner(session, f"test:sqla"),
        posargs=["--connector", f"{args.connector}"],
    )
    session.notify(
        find_session_runner(session, f"test:exasol"),
        posargs=["--connector", f"{args.connector}"],
    )
    session.notify(
        find_session_runner(session, f"test:regression"),
    )
    session.notify(find_session_runner(session, "db:stop"))


@nox.session(name="test:skipped", python=False)
def report_skipped(session: Session) -> None:
    """
    Runs all tests for all supported connectors and creates a csv report of skipped tests for each connector.

    Attention: This task expects a running test database (db-start).
    """
    with TemporaryDirectory() as tmp_dir:
        for connector in PROJECT_CONFIG.connectors:
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


# fmt: off
from exasol.toolbox.nox._documentation import (
    build_docs,
    build_multiversion,
    clean_docs,
    open_docs,
)

# fmt: on


@nox.session(name="docs:links", python=False)
def list_links(session: Session) -> None:
    """List all the links within the documentation."""
    for path, url in _urls(_documentation(PROJECT_ROOT)):
        session.log(f"Url: {url}, File: {path}")


@nox.session(name="docs:links:check", python=False)
def check_links(session: Session) -> None:
    """Checks whether all links in the documentation are accessible."""
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


# fmt: off
from exasol.toolbox.nox._documentation import (
    build_docs,
    build_multiversion,
    clean_docs,
    open_docs,
)


def _connector_matrix(config: Config):
    CONNECTORS = ['websocket']
    attr = "connectors"
    connectors = getattr(config, attr, CONNECTORS)
    if not hasattr(config, attr):
        _log.warning(
            "Config does not contain '%s' setting. Using default: %s",
            attr,
            CONNECTORS,
        )
    return {"connector": connectors}

from exasol.toolbox.nox._ci import (
    exasol_matrix,
    python_matrix,
)


@nox.session(name="matrix:all", python=False)
def full_matrix(session: Session) -> None:
    """Output the full build matrix for Python & Exasol versions as JSON."""
    import json

    from exasol.toolbox.nox._ci import (
        _exasol_matrix,
        _python_matrix,
    )
    matrix = _python_matrix(PROJECT_CONFIG)
    matrix.update(_exasol_matrix(PROJECT_CONFIG))
    matrix.update(_connector_matrix(PROJECT_CONFIG))
    print(json.dumps(matrix))

# fmt: on
