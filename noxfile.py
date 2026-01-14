from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from argparse import ArgumentParser
from collections import OrderedDict
from pathlib import Path
from tempfile import TemporaryDirectory

import nox

# imports all nox task provided by the toolbox
from exasol.toolbox.nox.tasks import *  # type: ignore
from nox import Session
from nox.sessions import SessionRunner

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["format:fix"]

from noxconfig import (
    PROJECT_CONFIG,
    Config,
)

SCRIPTS = PROJECT_CONFIG.root_path / "scripts"
sys.path.append(f"{SCRIPTS}")

_log = logging.getLogger(__name__)


def find_session_runner(session: Session, name: str) -> SessionRunner:
    """Helper function to find parameterized action by name"""
    for s, _ in session._runner.manifest.list_all_sessions():
        if name in s.signatures:
            return s
    session.error(f"Could not find a nox session by the name {name!r}")


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
        f"--rcfile={PROJECT_CONFIG.root_path / 'pyproject.toml'}",
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
        )
        return p

    args = parser().parse_args(session.posargs)
    connector = args.connector
    session.run(
        *_coverage_command(),
        "pytest",
        "--dropfirst",
        "--db",
        f"exasol-{connector}",
        f"{PROJECT_CONFIG.root_path / 'test' / 'integration' / 'sqlalchemy'}",
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
        )
        return p

    args = parser().parse_args(session.posargs)
    connector = args.connector
    session.run(
        *_coverage_command(),
        "pytest",
        "--dropfirst",
        "--db",
        f"exasol-{connector}",
        f"{PROJECT_CONFIG.root_path / 'test' / 'integration' / 'exasol'}",
        external=True,
    )


@nox.session(name="test:regression", python=False)
def regression_tests(session: Session) -> None:
    """Run regression tests"""
    session.run(
        *_coverage_command(),
        "pytest",
        f"{PROJECT_CONFIG.root_path / 'test' / 'integration' / 'regression'}",
    )


@nox.session(name="test:integration", python=False)
def integration_tests_for_sqlalchemy_exasol(session: Session) -> None:
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
        )
        p.add_argument(
            "--db-version",
            choices=PROJECT_CONFIG.exasol_versions,
            default=PROJECT_CONFIG.exasol_versions[0],
        )
        p.add_argument(
            "--coverage",
            action="store_true",
            help="This is only here for compatibility. Coverage will always be collected.",
        )
        return p

    coverage_file = PROJECT_CONFIG.root_path / ".coverage"
    coverage_file.unlink(missing_ok=True)

    args = parser().parse_args(session.posargs)
    session.notify(
        find_session_runner(session, "db:start"),
        posargs=["--db-version", f"{args.db_version}"],
    )
    session.notify(
        find_session_runner(session, "test:sqla"),
        posargs=["--connector", f"{args.connector}"],
    )
    session.notify(
        find_session_runner(session, "test:exasol"),
        posargs=["--connector", f"{args.connector}"],
    )
    session.notify(
        find_session_runner(session, "test:regression"),
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
            session.run(
                "pytest",
                "--dropfirst",
                "--db",
                f"exasol-{connector}",
                f"{PROJECT_CONFIG.root_path / 'test' / 'integration' / 'sqlalchemy'}",
                "--json-report",
                f"--json-report-file={report}",
                external=True,
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


def _connector_matrix(config: Config):
    connectors_list = ["websocket"]
    attr = "connectors"
    connectors = getattr(config, attr, connectors_list)
    if not hasattr(config, attr):
        _log.warning(
            "Config does not contain '%s' setting. Using default: %s",
            attr,
            connectors_list,
        )
    return {"connector": connectors}


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
    matrix["integration-group"] = ["exasol", "regression", "sqla"]
    print(json.dumps(matrix))


@nox.session(name="run:examples", python=False)
def run_examples(session: Session) -> None:
    """Execute examples, assuming a DB already is ready."""
    path = PROJECT_CONFIG.root_path / "examples"

    errors: OrderedDict[str, str] = OrderedDict()
    for file in sorted(path.rglob("*.py")):
        print(f"\033[32m{file.name}\033[0m")
        result = subprocess.run(["python", str(file)], capture_output=True, text=True)
        print(result.stdout)
        if stderr := result.stderr:
            # This records the last line in the traceback, which typically contains
            # the raised exception.
            errors[file.name] = stderr.strip().split("\n")[-1]

    if len(errors) > 0:
        escape_red = "\033[31m"
        print(escape_red + "Errors running examples:")
        for file_name, error in errors.items():
            print(f"- {file_name}: {error}")
        session.error(1)
