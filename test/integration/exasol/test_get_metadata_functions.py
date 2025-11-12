import pytest
from sqlalchemy import (
    create_engine,
    inspect,
    sql,
)
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.sql.ddl import (
    CreateSchema,
    DropSchema,
)
from sqlalchemy.sql.sqltypes import (
    INTEGER,
    VARCHAR,
)
from sqlalchemy.testing import (
    config,
    fixtures,
)

TEST_GET_METADATA_FUNCTIONS_SCHEMA = "test_get_metadata_functions_schema"
ENGINE_NONE_DATABASE = "ENGINE_NONE_DATABASE"
ENGINE_SCHEMA_DATABASE = "ENGINE_SCHEMA_DATABASE"
ENGINE_SCHEMA_2_DATABASE = "ENGINE_SCHEMA_2_DATABASE"


class MetadataTest(fixtures.TablesTest):
    __backend__ = True

    @classmethod
    def define_tables(cls, metadata):
        cls.schema = TEST_GET_METADATA_FUNCTIONS_SCHEMA
        cls.schema_2 = "test_get_metadata_functions_schema_2"
        with config.db.begin() as c:
            try:
                c.execute(DropSchema(cls.schema, cascade=True))
            except Exception as e:
                print(e)
                pass
            c.execute(CreateSchema(cls.schema))
            c.execute(
                sql.text(
                    "CREATE TABLE %s.t (pid1 int, pid2 int, name VARCHAR(20), age int, PRIMARY KEY (pid1,pid2))"
                    % cls.schema
                )
            )
            c.execute(
                sql.text(
                    "CREATE TABLE {schema}.s (id1 int primary key, fid1 int, fid2 int, age int, CONSTRAINT fk_test FOREIGN KEY (fid1,fid2) REFERENCES {schema}.t(pid1,pid2))".format(
                        schema=cls.schema
                    )
                )
            )
            cls.view_defintion = (
                "CREATE VIEW {schema}.v AS select * from {schema}.t".format(
                    schema=cls.schema
                )
            )
            c.execute(sql.text(cls.view_defintion))

            try:
                c.execute(DropSchema(cls.schema_2, cascade=True))
            except Exception as e:
                print(e)
                pass
            c.execute(CreateSchema(cls.schema_2))
            c.execute(
                sql.text(
                    "CREATE TABLE %s.t_2 (pid1 int, pid2 int, name VARCHAR(20), age int, PRIMARY KEY (pid1,pid2))"
                    % cls.schema_2
                )
            )
            c.execute(
                sql.text(
                    "CREATE VIEW {schema}.v_2 AS select * from {schema}.t_2".format(
                        schema=cls.schema_2
                    )
                )
            )
            c.execute(sql.text("COMMIT"))

            cls.engine_none_database = cls.create_engine_with_database_name(c, None)
            cls.engine_schema_database = cls.create_engine_with_database_name(
                c, cls.schema
            )
            cls.engine_schema_2_database = cls.create_engine_with_database_name(
                c, cls.schema_2
            )
            cls.engine_map = {
                ENGINE_NONE_DATABASE: cls.engine_none_database,
                ENGINE_SCHEMA_DATABASE: cls.engine_schema_database,
                ENGINE_SCHEMA_2_DATABASE: cls.engine_schema_2_database,
            }

    @classmethod
    def generate_url_with_database_name(cls, connection, new_database_name):
        database_url = config.db_url
        new_args = database_url.translate_connect_args()
        new_args["database"] = new_database_name
        new_database_url = URL.create(
            drivername=database_url.drivername, query=database_url.query, **new_args
        )
        return new_database_url

    @classmethod
    def create_engine_with_database_name(cls, connection, new_database_name):
        url = cls.generate_url_with_database_name(connection, new_database_name)
        engine = create_engine(url)
        return engine

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_schema_names(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            schema_names = dialect.get_schema_names(connection=c)
            assert self.schema in schema_names and self.schema_2 in schema_names

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_table_names(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            table_names = dialect.get_table_names(connection=c, schema=self.schema)
            assert table_names == ["s", "t"]

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_has_table_table_exists(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            has_table = dialect.has_table(
                connection=c,
                schema=self.schema,
                table_name="t",
            )
            assert has_table, f"Table {self.schema}.T was not found, but should exist"

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_has_table_table_exists_not(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            has_table = dialect.has_table(
                connection=c,
                schema=self.schema,
                table_name="not_exist",
            )
            assert (
                not has_table
            ), f"Table {self.schema}.not_exist was found, but should not exist"

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_view_names(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            view_names = dialect.get_view_names(connection=c, schema=self.schema)
            assert view_names == ["v"]

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_view_names_for_sys(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            view_names = dialect.get_view_names(connection=c, schema="sys")
            assert view_names == []

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_view_definition(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            view_definition = dialect.get_view_definition(
                connection=c,
                schema=self.schema,
                view_name="v",
            )
            assert view_definition == self.view_defintion

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_view_definition_view_name_none(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            with pytest.raises(NoSuchTableError):
                dialect.get_view_definition(
                    connection=c,
                    schema=self.schema,
                    view_name=None,
                )

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    @pytest.mark.parametrize(
        "schema,table",
        [
            pytest.param(
                TEST_GET_METADATA_FUNCTIONS_SCHEMA, "unknown", id="not existing table"
            ),
            pytest.param("NOT_A_SCHEMA", "s", id="not existing schema"),
        ],
    )
    def test_get_columns_raises_exception_for_no_table(
        self, schema, table, engine_name
    ):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            with pytest.raises(NoSuchTableError):
                dialect.get_columns(connection=c, table_name=table, schema=schema)

    def make_columns_comparable(
        self, column_list
    ):  # object equality doesn't work for sqltypes
        return sorted(
            ({k: str(v) for k, v in column.items()} for column in column_list),
            key=lambda k: k["name"],
        )

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_columns(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            columns = dialect.get_columns(
                connection=c,
                schema=self.schema,
                table_name="t",
            )
            expected = [
                {
                    "default": None,
                    "is_distribution_key": False,
                    "name": "pid1",
                    "nullable": False,
                    "type": INTEGER(),
                },
                {
                    "default": None,
                    "is_distribution_key": False,
                    "name": "pid2",
                    "nullable": False,
                    "type": INTEGER(),
                },
                {
                    "default": None,
                    "is_distribution_key": False,
                    "name": "name",
                    "nullable": True,
                    "type": VARCHAR(length=20),
                },
                {
                    "default": None,
                    "is_distribution_key": False,
                    "name": "age",
                    "nullable": True,
                    "type": INTEGER(),
                },
            ]

            assert self.make_columns_comparable(
                expected
            ) == self.make_columns_comparable(columns)

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_columns_table_name_none(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            columns = dialect.get_columns(
                connection=c,
                schema=self.schema,
                table_name=None,
            )
            assert columns == []

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    @pytest.mark.parametrize(
        "schema,table",
        [
            pytest.param(
                TEST_GET_METADATA_FUNCTIONS_SCHEMA, "unknown", id="not existing table"
            ),
            pytest.param("NOT_A_SCHEMA", "s", id="not existing schema"),
        ],
    )
    def test_get_pk_constraint_raises_exception_for_no_table(
        self, schema, table, engine_name
    ):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            with pytest.raises(NoSuchTableError):
                dialect.get_pk_constraint(connection=c, table_name=table, schema=schema)

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_pk_constraint(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            pk_constraint = dialect.get_pk_constraint(
                connection=c,
                schema=self.schema,
                table_name="t",
            )
            assert pk_constraint["constrained_columns"] == [
                "pid1",
                "pid2",
            ] and pk_constraint["name"].startswith("sys_")

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_pk_constraint_table_name_none(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            pk_constraint = dialect.get_pk_constraint(
                connection=c,
                schema=self.schema,
                table_name=None,
            )
            assert pk_constraint is None

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    @pytest.mark.parametrize(
        "schema,table",
        [
            pytest.param(
                TEST_GET_METADATA_FUNCTIONS_SCHEMA, "unknown", id="not existing table"
            ),
            pytest.param("NOT_A_SCHEMA", "s", id="not existing schema"),
        ],
    )
    def test_get_foreign_keys_raises_exception_for_no_table(
        self, schema, table, engine_name
    ):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            with pytest.raises(NoSuchTableError):
                dialect.get_foreign_keys(connection=c, table_name=table, schema=schema)

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_foreign_keys(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            foreign_keys = dialect.get_foreign_keys(
                connection=c,
                schema=self.schema,
                table_name="s",
            )
            expected = [
                {
                    "name": "fk_test",
                    "constrained_columns": ["fid1", "fid2"],
                    "referred_schema": "test_get_metadata_functions_schema",
                    "referred_table": "t",
                    "referred_columns": ["pid1", "pid2"],
                }
            ]

            assert foreign_keys == expected

    @pytest.mark.parametrize(
        "engine_name",
        [ENGINE_NONE_DATABASE, ENGINE_SCHEMA_DATABASE, ENGINE_SCHEMA_2_DATABASE],
    )
    def test_get_foreign_keys_table_name_none(self, engine_name):
        with self.engine_map[engine_name].begin() as c:
            dialect = inspect(c).dialect
            foreign_keys = dialect.get_foreign_keys(
                connection=c,
                schema=self.schema,
                table_name=None,
            )
            assert foreign_keys == []
