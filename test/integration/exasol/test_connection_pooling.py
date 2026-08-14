from collections.abc import Iterator

import pytest
import sqlalchemy
from sqlalchemy import (
    create_engine,
)
from sqlalchemy.testing import (
    config,
    fixtures,
)


class Pooling(fixtures.TestBase):
    @classmethod
    def exception_trace(cls, ex: Exception) -> Iterator[str]:
        """
        Return a sequence of strings, each representing one of the exceptions
        linked by __cause__ and containing the exceptions's message.
        """

        current = ex
        cause = "Initial exception"
        while current:
            yield (f"{cause}: {type(current)}: {current}")
            current = current.__cause__
            cause = "Cause"

    @classmethod
    def create_engine(cls, **kwargs) -> sqlalchemy.Engine:
        args = {
            "url": config.db.url,
            "poolclass": sqlalchemy.QueuePool,
            "pool_size": 2,
            "max_overflow": 0,
            "pool_recycle": 3600,  # recycle connections after an hour
            "pool_pre_ping": True,  # test connection before reuse
        } | kwargs
        return create_engine(**args)

    def test_exception(self) -> None:
        """
        Verify that the exception raised by a SQLALchemy Engine using a
        Connection Pool does not reveal any secret.
        """

        url = config.db.url.set(password="wrong password")
        with pytest.raises(sqlalchemy.exc.DBAPIError) as ex:
            engine = self.create_engine(url=url).connect()
        trace = "\n".join(self.exception_trace(ex.value))
        assert "wrong password" not in trace
