from dataclasses import dataclass
from typing import Any

import sqlalchemy

from examples.config import ENGINE


@dataclass
class ExaParam:
    name: str
    session_value: str
    system_value: str

    QUERY = sqlalchemy.text("SELECT * FROM EXA_PARAMETERS")

    @classmethod
    def alter_statement(
        cls,
        name: str,
        value: str,
        scope: str = "SESSION",
    ) -> sqlalchemy.TextClause:
        return sqlalchemy.text(f"ALTER {scope} SET {name} = '{value}'")

    @property
    def differs(self) -> bool:
        return self.session_value != self.system_value

    @property
    def alter_session(self) -> sqlalchemy.TextClause:
        return self.alter_statement(self.name, self.system_value)


with ENGINE.connect() as con:
    con.execute(ExaParam.alter_statement("IDLE_TIMEOUT", "80000"))
    altered_parameters = (
        exa_param for row in con.execute(ExaParam.QUERY).fetchall()
        if (exa_param := ExaParam(*row)).differs
    )
    for p in altered_parameters:
        reset = p.alter_session
        print(f'{reset}')
        con.execute(reset)
