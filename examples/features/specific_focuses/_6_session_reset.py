from dataclasses import dataclass

import sqlalchemy

from examples.config import SQL_ALCHEMY

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


# 2. Create an engine using a connection pool
engine = SQL_ALCHEMY.create_engine(
    poolclass=sqlalchemy.QueuePool,
    pool_size=10,
    max_overflow=2,
    pool_recycle=3600,  # recycle connections after an hour
    pool_pre_ping=True,  # test connection liveness before use
)


# 3. Listen when a connection is reset
def on_reset(con, connection_record, reset_state):
    with con.cursor() as cur:
        # Retrieve changed parameters
        cur.execute(ExaParam.QUERY)
        altered_parameters = (
            exa_param for row in cur.fetchall() if (exa_param := ExaParam(*row)).differs
        )
        # Reset parameter values
        for p in altered_parameters:
            reset = p.alter_session
            print(f"{reset}")
            cur.execute(reset)


sqlalchemy.event.listen(engine, "reset", on_reset)

with engine.connect() as con:
    # 4. Intentionally modify one parameter to showcase an example
    con.execute(ExaParam.alter_statement("IDLE_TIMEOUT", "80000"))


# 5. Rely on Event handler on_reset() to reset changed parameters to their
# resp. system values.
