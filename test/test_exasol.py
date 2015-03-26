# -*- coding: UTF-8 -*-
from sqlalchemy import MetaData, Table, Column, Integer, String, Date
from sqlalchemy.testing import fixtures, config
from sqlalchemy import testing, inspect
from sqlalchemy.schema import DropConstraint, AddConstraint

import datetime

from sqlalchemy_exasol.base import RESERVED_WORDS
from sqlalchemy_exasol.merge import merge
from sqlalchemy_exasol.constraints import DistributeByConstraint

class MergeTest(fixtures.TablesTest):

    #run_deletes = 'each'

    __backend__ = True

    __engine_options__ = {"implicit_returning": False}

    @classmethod
    def define_tables(cls, metadata):
        Table('t', metadata,
            Column('id', Integer),
            Column('name', String(20)),
            Column('age', Integer)
        )
        Table('s', metadata,
            Column('id', Integer),
            Column('age', Integer)
        )

    def test_merge_update(self):
        t = self.tables.t
        s = self.tables.s

        config.db.execute(
            t.insert(),
            [dict(id=1, age=None, name='Ulf')]
        )
        config.db.execute(
            s.insert(),
            [dict(id=1, age=10)]
        )

        m = merge(t, s, t.c.id == s.c.id).update()
        mr = config.db.execute(m)

        r = config.db.execute(t.select()).first()
        assert r.age == 10

    def test_merge_update_where(self):
        t = self.tables.t
        s = self.tables.s

        config.db.execute(
            t.insert(),
            [
                dict(id=1, name='Ulf'),
                dict(id=2, name='Karl'),
            ]
        )
        config.db.execute(
            s.insert(),
            [
                dict(id=1, age=10),
                dict(id=2, age=20),
                dict(id=3, age=30),
            ]
        )

        m = merge(t, s, t.c.id == s.c.id).update(
                    values={t.c.age: s.c.age},
                    where=t.c.id == s.c.id
                )
        mr = config.db.execute(m)

        r = config.db.execute(t.select().where(t.c.id == 1)).first()
        assert r.age == 10
        r = config.db.execute(t.select().where(t.c.id == 2)).first()
        assert r.age == 20
        r = config.db.execute(t.select().where(t.c.id == 3)).fetchall()
        assert len(r) == 0

    def test_merge_insert(self):
        t = self.tables.t
        s = self.tables.s

        config.db.execute(
            t.insert(),
            [
                dict(id=1, name='Ulf'),
            ]
        )
        config.db.execute(
            s.insert(),
            [
                dict(id=1, age=10),
                dict(id=2, age=20),
            ]
        )

        m = merge(t, s, t.c.id == s.c.id).insert()
        config.db.execute(m)
        r = config.db.execute(t.select()).fetchall()
        assert len(r) == 2

    def test_merge_delete_where(self):
        t = self.tables.t
        s = self.tables.s

        config.db.execute(
            t.insert(),
            [
                dict(id=1, name='Ulf'),
            ]
        )
        config.db.execute(
            s.insert(),
            [
                dict(id=1, age=10),
                dict(id=2, age=20),
                dict(id=3, age=2),
            ]
        )

        m = merge(t, s, t.c.id == s.c.id).insert(
                where=s.c.age > 5
            )
        config.db.execute(m)
        r = config.db.execute(t.select()).fetchall()
        assert len(r) == 2

    def test_merge_delete(self):
        t = self.tables.t
        s = self.tables.s

        config.db.execute(
            t.insert(),
            [
                dict(id=1, name='Ulf'),
                dict(id=4, name='Peter'),
            ]
        )
        config.db.execute(
            s.insert(),
            [
                dict(id=1, age=10),
                dict(id=2, age=20),
            ]
        )

        m = merge(t, s, t.c.id == s.c.id).delete()
        config.db.execute(m)
        r = config.db.execute(t.select()).fetchall()
        assert len(r) == 1

    def test_merge_update_insert(self):
        t = self.tables.t
        s = self.tables.s

        config.db.execute(
            t.insert(),
            [
                dict(id=1, name='Ulf'),
            ]
        )
        config.db.execute(
            s.insert(),
            [
                dict(id=1, age=10),
                dict(id=2, age=20),
            ]
        )

        m = merge(t, s, t.c.id == s.c.id).update(
                values={t.c.age: s.c.age}
            ).insert()
        config.db.execute(m)
        r = config.db.execute(t.select()).fetchall()
        assert len(r) == 2

    def test_merge_update_delete(self):
        t = self.tables.t
        s = self.tables.s

        config.db.execute(
            t.insert(),
            [dict(id=1, name='Ulf')]
        )
        config.db.execute(
            s.insert(),
            [dict(id=1, age=10)]
        )

        m = merge(t, s, t.c.id == s.c.id).update(
                values={t.c.age: s.c.age}
            ).delete()
        config.db.execute(m)
        r = config.db.execute(t.select()).fetchall()
        assert len(r) == 0

    def test_merge_update_delete_where(self):
        t = self.tables.t
        s = self.tables.s

        config.db.execute(
            t.insert(),
            [dict(id=1, name='Ulf')]
        )
        config.db.execute(
            s.insert(),
            [dict(id=1, age=10)]
        )

        m = merge(t, s, t.c.id == s.c.id).update(
                values={t.c.age: s.c.age}
            ).delete(t.c.id == s.c.id)
        config.db.execute(m)
        r = config.db.execute(t.select()).fetchall()
        assert len(r) == 0


class DefaultsTest(fixtures.TablesTest):
    __backend__ = True

    @classmethod
    def define_tables(cls, metadata):
        default_date = datetime.date(1900, 1, 1)
        Table('t', metadata,
            Column('id', Integer),
            Column('name', String(20)),
            Column('active_from', Date, default=default_date)
        )

    def test_insert_with_default_value(self):
        t = self.tables.t

        config.db.execute(
            t.insert(),
            [{'name': 'Henrik'}]
        )
        (_, _, active_from) = config.db.execute(t.select()).fetchone()
        assert active_from == datetime.date(1900, 1, 1)

class KeywordTest(fixtures.TablesTest):
    
    __backend__ = True

    def test_keywords(self):
        keywords = config.db.execute('select distinct(lower(keyword)) as keyword ' +
            'from SYS.EXA_SQL_KEYWORDS where reserved = True order by keyword').fetchall()
        db_keywords = set([k[0] for k in keywords])
        assert db_keywords <= RESERVED_WORDS

class ConstraintsTest(fixtures.TablesTest):
    __backend__ = True

    @classmethod
    def define_tables(cls, metadata):
        Table('t', metadata,
           Column('a', Integer),
           Column('b', Integer),
           Column('c', Integer),
           DistributeByConstraint('a', 'b')
        )


    def test_distribute_by_constraint(self):
        try:
           reflected = Table('t', MetaData(testing.db), autoload=True)
        except:
           assert False
        #TODO: check that reflected table object is identical
        # i.e. contains the constraint
        insp = inspect(testing.db)
        for c in insp.get_columns('t'):
            if not (c['name'] == 'c'):
                assert c['is_distribution_key'] == True
            else:
                assert c['is_distribution_key'] == False

    def test_alter_table_distribute_by(self):
        dbc = DistributeByConstraint('a', 'b')
        self.tables.t.append_constraint(dbc)

        config.db.execute(DropConstraint(dbc))

        insp = inspect(testing.db)
        for c in insp.get_columns('t'):
            assert c['is_distribution_key'] == False

        config.db.execute(AddConstraint(dbc))

        insp = inspect(testing.db)
        for c in insp.get_columns('t'):
            if not (c['name'] == 'c'):
                assert c['is_distribution_key'] == True
            else:
                assert c['is_distribution_key'] == False

