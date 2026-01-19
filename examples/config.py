from collections.abc import (
    Mapping,
    Sequence,
)

from pydantic import (
    Field,
    SecretStr,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from sqlalchemy import (
    URL,
    Engine,
    create_engine,
)

DEFAULT_SCHEMA_NAME = "EXAMPLE_SCHEMA"


class ConnectionConfig(BaseSettings):
    """
    The values default to the default Exasol Docker DB, but they can
    be overridden individually by environment variables.

    The environment variable to use to override the default value is
    given in `validation_alias` for each attribute. Note that you may
    need to set an exported environment variable for it to properly work.
    """

    username: str = Field(default="sys", validation_alias="EXA_USERNAME")
    password: SecretStr = Field(
        default=SecretStr("exasol"), validation_alias="EXA_PASSWORD"
    )
    host: str = Field(default="127.0.0.1", validation_alias="EXA_HOST")
    port: int = Field(default=8563, validation_alias="EXA_PORT")
    database: str | None = None
    query: Mapping[str, Sequence[str] | str] = Field(
        default={}, validation_alias="EXA_QUERY"
    )

    model_config = SettingsConfigDict(env_prefix="EXA_", case_sensitive=False)

    @model_validator(mode="after")
    def set_query_default(self) -> "ConnectionConfig":
        """
        For security purposes, `self.query` should NEVER be empty for a
        PRODUCTION system. Please refer to our Security page:
        - https://exasol.github.io/sqlalchemy-exasol/master/user_guide/configuration/security.html
        to find an option appropriate for your use case.
        """
        if self.query == {}:
            # This "fallback" value should NEVER be used for a PRODUCTION system.
            self.query = {"FINGERPRINT": "nocertcheck"}
        return self


class SqlAlchemyFactory(BaseSettings):
    config: ConnectionConfig

    def create_url(self) -> URL:
        """
        Create a new `URL` instance, which is used in `create_engine`. The parameters
        to URL are described further on:
            https://exasol.github.io/sqlalchemy-exasol/master/user_guide/configuration/connection_parameters.html
        """
        return URL.create(
            drivername="exa+websocket",
            username=self.config.username,
            password=self.config.password.get_secret_value(),
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            query=self.config.query,
        )

    def create_engine(self) -> Engine:
        """
        Create a new `Engine` instance. This is used to create a connection via
        `connect()`. Throughout the examples, the default values for `create_engine()`
        are used, but other options are described on:
            https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine
        """

        url = self.create_url()
        return create_engine(url)


CONNECTION_CONFIG = ConnectionConfig()
SQL_ALCHEMY = SqlAlchemyFactory(config=CONNECTION_CONFIG)
ENGINE = SQL_ALCHEMY.create_engine()

if __name__ == "__main__":
    print(f"CONNECTION_DICT: {CONNECTION_CONFIG.model_dump_json(indent=4)}")
