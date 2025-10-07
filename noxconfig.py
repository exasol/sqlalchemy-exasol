from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from exasol.toolbox.nox.plugin import hookimpl


class StartDB:

    @hookimpl
    def pre_integration_tests_hook(self, session, config, context):
        port = context.get("port", 8563)
        db_version = context.get("db_version", "7.1.17")
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


@dataclass(frozen=True)
class Config:
    root: Path = Path(__file__).parent
    doc: Path = Path(__file__).parent / "doc"
    source: Path = Path("sqlalchemy_exasol")
    version_file: Path = Path(__file__).parent / "sqlalchemy_exasol" / "version.py"
    path_filters: Iterable[str] = (
        "dist",
        ".eggs",
        "venv",
    )
    environment_name = "test"
    db_port = 8563
    bucketfs_port = 2580
    connectors = ["pyodbc", "turbodbc", "websocket"]
    python_versions = ["3.10", "3.11", "3.12", "3.13"]
    exasol_versions = ["7.1.30", "8.34.0", "2025.1.0"]

    plugins = [StartDB, StopDB]


PROJECT_CONFIG = Config()
