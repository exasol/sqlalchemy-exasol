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
    connectors: list[str] = ["pyodbc", "websocket"]
    plugins: list = [StartDB, StopDB]


PROJECT_CONFIG = Config(
    # PTB 1.12.0 still supports Python 3.9, so we override the python_versions
    python_versions=("3.10", "3.11", "3.12", "3.13"),
)
