import os
import urllib.error
from contextlib import contextmanager
from email import policy
from email.parser import BytesParser
from itertools import repeat
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from urllib import request

import nox
from pyodbc import connect
from urlscan import urlchoose, urlscan

PROJECT_ROOT = Path(__file__).parent

# default actions to be run if nothing is explicitly specified with the -s option
nox.options.sessions = ["verify(connector='pyodbc')"]


class Settings:
    ITDE = PROJECT_ROOT / ".." / "integration-test-docker-environment"
    ODBC_DRIVER = PROJECT_ROOT / "driver" / "libexaodbc-uo2214lv1.so"
    CONNECTORS = ("pyodbc", "turbodbc")
    ENVIRONMENT_NAME = "test"
    DB_PORT = 8888
    BUCKETFS_PORT = 6666


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


def find_session_runner(session: nox.Session, name: str):
    """Helper function to find parameterized action by name"""
    for s, _ in session._runner.manifest.list_all_sessions():
        if name in s.signatures:
            return s
    session.error(f"Could not find a nox session by the name {name!r}")


def transaction(connection, sql_statements):
    cur = connection.cursor()
    for statement in sql_statements:
        cur.execute(statement)
    cur.commit()
    cur.close()


@contextmanager
def environment(env_vars):
    _env = os.environ.copy()
    os.environ.update(env_vars)
    yield os.environ
    os.environ.clear()
    os.environ.update(_env)


@contextmanager
def temporary_odbc_config(config):
    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        config_dir = tmp_dir / "odbcconfig"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "odbcinst.ini"
        with open(config_file, "w") as f:
            f.write(config)
        yield config_file


@contextmanager
def odbcconfig():
    with temporary_odbc_config(
        ODBCINST_INI_TEMPLATE.format(driver=Settings.ODBC_DRIVER)
    ) as cfg:
        env_vars = {"ODBCSYSINI": f"{cfg.parent.resolve()}"}
        with environment(env_vars) as env:
            yield cfg, env


@nox.session
@nox.parametrize("connector", Settings.CONNECTORS)
def verify(session, connector):
    """Prepare and run all available tests"""
    session.notify(find_session_runner(session, "db-start"))
    session.notify(
        find_session_runner(session, f"integration(connector='{connector}')")
    )
    session.notify(find_session_runner(session, "db-stop"))


@nox.session(name="db-start", reuse_venv=True)
def start_db(session):
    """Start the test database"""

    def start():
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
                "--db-mem-size",
                "4GB",
                external=True,
            )

    def populate():
        with odbcconfig():
            settings = {
                "driver": "EXAODBC",
                "server": "localhost:8888",
                "user": "sys",
                "password": "exasol",
            }
            connection = connect(
                "".join(
                    [
                        "DRIVER={driver};",
                        "EXAHOST={server};",
                        "UID={user};",
                        "PWD={password}",
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


@nox.session(name="db-stop", reuse_venv=True)
def stop_db(session):
    """Stop the test database"""
    session.run("docker", "kill", "db_container_test", external=True)
    session.run("docker", "kill", "test_container_test", external=True)


@nox.session
@nox.parametrize("connector", Settings.CONNECTORS)
def integration(session, connector):
    """Run(s) the integration tests for a specific connector. Expects a test database to be available."""

    with odbcconfig() as (config, env):
        uri = "".join(
            [
                "exa+{connector}:",
                "//sys:exasol@localhost:{db_port}",
                "/TEST?CONNECTIONLCALL=en_US.UTF-8&DRIVER=EXAODBC",
            ]
        ).format(connector=connector, db_port=Settings.DB_PORT)
        session.run("pytest", "--dropfirst", "--dburi", uri, external=True, env=env)


def _documentation():
    """Returns an iterator over all documentation files of the project"""
    docs = PROJECT_ROOT.glob("**/*.rst")

    def _deny_filter(path):
        return not ("venv" in path.parts)

    return filter(lambda path: _deny_filter(path), docs)


def _urls(files):
    """Returns an iterator over all urls contained in the provided files"""

    def should_filter(url):
        _filtered = []
        return url.startswith("mailto") or url in _filtered

    for file in files:
        with open(file, "rb") as f:
            content = BytesParser(policy=policy.default.clone(utf8=True)).parse(f)
            selector = urlchoose.URLChooser(
                urlscan.msgurls(content), dedupe=False, reverse=False, shorten=False
            )
            yield from zip(
                repeat(file), filter(lambda url: not should_filter(url), selector.urls)
            )


def _check(url):
    """Checks if an url is still working (can be accessed)"""
    try:
        # User-Agent needs to be faked otherwise some webpages will deny access with a 403
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        result = request.urlopen(req)
        return result.code, f"{result.msg}"
    except urllib.error.HTTPError as ex:
        return ex.status, f"{ex}"


@nox.session(name="check-links", python=None)
def check_links(session):
    """Checks weather or not all links in the documentation can be accessed"""
    errors = []
    for path, url in _urls(_documentation()):
        status, details = _check(url)
        if status != 200:
            errors.append((path, url, status, details))

    if errors:
        session.error(
            "\n"
            + "\n".join((f"Url: {e[1]}, File: {e[0]}, Error: {e[3]}" for e in errors))
        )


@nox.session(name="list-links", python=None)
def list_links(session):
    """List all links within the documentation"""
    for path, url in _urls(_documentation()):
        session.log(f"Url: {url}, File: {path}")
