from dataclasses import dataclass
from typing import Any

import sqlalchemy

from examples.config import ENGINE


# 1. Define a class to conveniently reset EXA_PARAMETERS to
# their resp. system values

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
    # 2. Intentionally modify one parameter to showcase an example
    con.execute(ExaParam.alter_statement("IDLE_TIMEOUT", "80000"))

    # 3. Retrieve changed parameters
    altered_parameters = (
        exa_param for row in con.execute(ExaParam.QUERY).fetchall()
        if (exa_param := ExaParam(*row)).differs
    )
    # 4. Reset parameter values
    for p in altered_parameters:
        reset = p.alter_session
        print(f'{reset}')
        con.execute(reset)
