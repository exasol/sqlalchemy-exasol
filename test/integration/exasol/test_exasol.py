import datetime

import pytest
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy import exc as sa_exc
from sqlalchemy import (
    extract,
    inspect,
    or_,
    select,
    sql,
    testing,
)
from sqlalchemy.schema import (
    AddConstraint,
    DropConstraint,
)
from sqlalchemy.testing import (
    config,
    fixtures,
)

from sqlalchemy_exasol.base import (
    RESERVED_WORDS,
    EXAExecutionContext,
)
from sqlalchemy_exasol.constraints import DistributeByConstraint
from sqlalchemy_exasol.util import raw_sql


class DefaultsTest(fixtures.TablesTest):
    __backend__ = True

    @classmethod
    def define_tables(cls, metadata):
        default_date = datetime.date(1900, 1, 1)
        Table(
            "t",
            metadata,
            Column("id", Integer),
            Column("name", String(20)),
            Column("active_from", Date, default=default_date),
        )

    def test_insert_with_default_value(self):
        t = self.tables.t

        with config.db.begin() as conn:
            conn.execute(t.insert(), [{"name": "Henrik"}])

        with config.db.connect() as conn:
            _, _, active_from = conn.execute(t.select()).fetchone()

        assert active_from == datetime.date(1900, 1, 1)


class KeywordTest(fixtures.TablesTest):
    __backend__ = True

    def test_keywords(self):
        with config.db.connect() as conn:
            keywords = conn.execute(
                sql.text(
                    "select distinct(lower(keyword)) as keyword "
                    + "from SYS.EXA_SQL_KEYWORDS where reserved = True order by keyword"
                )
            ).fetchall()

        db_keywords = {k[0] for k in keywords}

        assert db_keywords >= RESERVED_WORDS


class AutocommitTest(fixtures.TablesTest):
    __backend__ = False

    def test_trunctate(self):
        ctx = EXAExecutionContext()
        assert ctx.should_autocommit_text("truncate test;")


class ConstraintsTest(fixtures.TablesTest):
    __backend__ = True

    @classmethod
    def define_tables(cls, metadata):
        Table(
            "t",
            metadata,
            Column("a", Integer),
            Column("b", Integer),
            Column("c", Integer),
            DistributeByConstraint("a", "b"),
        )

    def test_distribute_by_constraint(self):
        with testing.db.connect() as conn:
            Table("t", MetaData(), autoload_with=conn)
        # TODO: check that reflected table object is identical
        # i.e. contains the constraint
        insp = inspect(testing.db)
        for c in insp.get_columns("t"):
            if not (c["name"] == "c"):
                assert c["is_distribution_key"] == True
            else:
                assert c["is_distribution_key"] == False

    def test_alter_table_distribute_by(self):
        dbc = DistributeByConstraint("a", "b")
        self.tables.t.append_constraint(dbc)

        with config.db.begin() as conn:
            conn.execute(DropConstraint(dbc))

        insp = inspect(testing.db)
        for c in insp.get_columns("t"):
            assert c["is_distribution_key"] == False

        with config.db.begin() as conn:
            conn.execute(AddConstraint(dbc))

        insp = inspect(testing.db)
        for c in insp.get_columns("t"):
            if not (c["name"] == "c"):
                assert c["is_distribution_key"] == True
            else:
                assert c["is_distribution_key"] == False


class UtilTest(fixtures.TablesTest):
    __backend__ = True

    @classmethod
    def define_tables(cls, metadata):
        Table(
            "t",
            metadata,
            Column("id", Integer),
            Column("name", String(20)),
            Column("age", Integer),
            Column("day", Date),
            Column("created", DateTime),
        )

    def test_raw_sql(self):
        restriction = or_(
            self.tables.t.c.id == 1,
            self.tables.t.c.name == "bob",
            self.tables.t.c.day == datetime.date(2017, 1, 1),
            self.tables.t.c.created == datetime.datetime(2017, 1, 1, 12, 0, 0),
        )
        sel = self.tables.t.select().where(restriction)
        assert raw_sql(sel) == (
            'SELECT t.id, t.name, t.age, t."day", t.created \n'
            "FROM t \n"
            "WHERE t.id = 1 OR t.name = 'bob' OR t.\"day\" = to_date('2017-01-01', 'YYYY-MM-DD') OR t.created = to_timestamp('2017-01-01 12:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.FF6')"
        )


class ExtractTest(fixtures.TablesTest):
    __backend__ = True

    @classmethod
    def define_tables(cls, metadata):
        Table(
            "t",
            metadata,
            Column("id", Integer),
            Column("created", DateTime),
            Column("date_value", Date),
        )

    @classmethod
    def insert_data(cls, connection):
        connection.execute(
            cls.tables.t.insert(),
            [
                {
                    "id": 1,
                    "created": datetime.datetime(2017, 3, 5, 12, 34, 56),
                    "date_value": datetime.date(2017, 3, 5),
                }
            ],
        )

    @testing.combinations(
        ("year", 2017),
        ("month", 3),
        ("day", 5),
        ("hour", 12),
        ("minute", 34),
        ("second", 56),
        argnames="field,expected",
    )
    def test_extract_returns_date_part(self, field, expected):
        t = self.tables.t
        with config.db.connect() as conn:
            result = conn.execute(select(extract(field, t.c.created))).scalar()
        assert result == expected

    # Unlike the test above, this verifies EXTRACT behavior for a DATE column,
    # which supports only year, month, and day.
    @testing.combinations(
        ("year", 2017),
        ("month", 3),
        ("day", 5),
        argnames="field,expected",
    )
    def test_extract_returns_date_part_from_date(self, field, expected):
        t = self.tables.t
        with config.db.connect() as conn:
            result = conn.execute(select(extract(field, t.c.date_value))).scalar()
        assert result == expected

    @testing.combinations(
        ("hour",),
        ("minute",),
        ("second",),
        argnames="field",
    )
    def test_extract_rejects_timestamp_date_parts_from_date(self, field):
        t = self.tables.t
        statement = select(extract(field, t.c.date_value))
        with config.db.connect() as conn:
            with pytest.raises(sa_exc.DBAPIError):
                conn.scalar(statement)
