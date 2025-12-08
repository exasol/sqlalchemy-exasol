from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from exasol.toolbox.config import BaseConfig
from exasol.toolbox.nox.plugin import hookimpl


class StartDB:

    @hookimpl
    def pre_integration_tests_hook(self, session, config, context):
        port = context.get("port", 8563)
        db_version = context.get("db_version", "2025.1.0")
        session.run(
            "itde",
            "spawn-test-environment",
            "--create-certificates",
            "--environment-name",
            "test",
            "--database-port-forward",
            f"{port}",
            "--bucketfs-port-forward",
            "2580",
            "--docker-db-image-version",
            db_version,
            "--db-mem-size",
            "4GB",
            external=True,
        )


class StopDB:

    @hookimpl
    def post_integration_tests_hook(self, session, config, context):
        session.run("docker", "kill", "db_container_test", external=True)


class Config(BaseConfig):
    root: Path = Path(__file__).parent
    doc: Path = Path(__file__).parent / "doc"
    source: Path = Path("sqlalchemy_exasol")
    version_file: Path = Path(__file__).parent / "sqlalchemy_exasol" / "version.py"
    path_filters: Iterable[str] = (
        "dist",
        ".eggs",
        "venv",
    )
    environment_name: str = "test"
    db_port: int = 8563
    bucketfs_port: int = 2580
    connectors: list[str] = ["websocket"]
    plugins: list = [StartDB, StopDB]


PROJECT_CONFIG = Config(
    # pytest-exasol-backend requires Python <3.14. When pytest-exasol-backend has been
    # updated to allow Python 3.14, then we can remove the override for python_versions.
    # Keeping track of pytest-exasol-backend and removing the override is tracked in
    # this issue:
    #     https://github.com/exasol/sqlalchemy-exasol/issues/674
    python_versions=("3.10", "3.11", "3.12", "3.13"),
    # Override to restrict to existing version on dockerhub. To be resolved in
    # PTB issue:
    #    https://github.com/exasol/python-toolbox/issues/604
    exasol_versions=("7.1.30", "8.29.13", "2025.1.8"),
)
