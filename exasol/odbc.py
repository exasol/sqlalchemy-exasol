from __future__ import annotations

import os
from collections.abc import (
    Iterable,
    Iterator,
    MutableMapping,
)
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from pyodbc import Connection

PROJECT_ROOT = Path(__file__).parent / ".."

ODBC_DRIVER = PROJECT_ROOT / "driver" / "libexaodbc-uo2214lv2.so"

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
def odbcconfig(driver: Path) -> Iterator[tuple[Path, MutableMapping[str, str]]]:
    with temporary_odbc_config(ODBCINST_INI_TEMPLATE.format(driver=driver)) as cfg:
        env_vars = {"ODBCSYSINI": f"{cfg.parent.resolve()}"}
        with environment(env_vars) as env:
            yield cfg, env
