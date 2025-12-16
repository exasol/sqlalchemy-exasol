from __future__ import annotations

from pathlib import Path

from exasol.toolbox.config import BaseConfig
from exasol.toolbox.nox.plugin import hookimpl
from pydantic import computed_field


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
    environment_name: str = "test"
    db_port: int = 8563
    bucketfs_port: int = 2580
    connectors: list[str] = ["websocket"]

    @computed_field  # type: ignore[misc]
    @property
    def source_code_path(self) -> Path:
        """
        Path to the source code of the project.

        In sqlalchemy-exasol, this needs to be overridden due to a custom directory setup.
        This will be addressed in:
            https://github.com/exasol/sqlalchemy-exasol/issues/682
        """
        return self.root_path / self.project_name


PROJECT_CONFIG = Config(
    root_path=Path(__file__).parent,
    project_name="sqlalchemy_exasol",
    plugins_for_nox_sessions=(StartDB, StopDB),
    # pytest-exasol-backend requires Python <3.14. When pytest-exasol-backend has been
    # updated to allow Python 3.14, then we can remove the override for python_versions.
    # Keeping track of pytest-exasol-backend and removing the override is tracked in
    # this issue:
    #     https://github.com/exasol/sqlalchemy-exasol/issues/674
    python_versions=("3.10", "3.11", "3.12", "3.13"),
)
