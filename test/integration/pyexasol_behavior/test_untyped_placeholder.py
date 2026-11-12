"""PyExasol-level tests for placeholders whose type the database cannot infer.

For ``SELECT ? FROM DUAL`` there is no column to infer a type from, so the database
reports the placeholder as ``VARCHAR(2000000)``. PyExasol >= 4.0.0 validates such a
placeholder like a declared VARCHAR column and rejects every non-``str`` value.

These tests use PyExasol directly (no SQLAlchemy), e.g. as a reproduction for a
PyExasol issue. They live outside ``test/integration/exasol`` and
``test/integration/sqlalchemy`` because the SQLAlchemy pytest plugin used there only
collects ``TestBase`` classes.
"""

import decimal
import uuid

import pytest

UNTYPED = {"type": "VARCHAR", "size": 2000000, "characterSet": "UTF8"}
SELECT_UNTYPED = "SELECT ? FROM DUAL"
SELECT_DECIMAL = (
    "SELECT 1 FROM (SELECT CAST(1.5 AS DECIMAL(10, 4)) AS c FROM DUAL) WHERE c = ?"
)
NUMBERS = [decimal.Decimal("15.7563"), 15, 1.5]

# Complete parameter metadata of the prepare responses, written out in full.
# ``SELECT ? FROM DUAL``: no column to infer a type from, default VARCHAR.
RESPONSE_UNTYPED = {
    "numColumns": 1,
    "columns": [
        {
            "name": "",
            "dataType": {"type": "VARCHAR", "size": 2000000, "characterSet": "UTF8"},
        }
    ],
}
# ``... WHERE c = ?`` with ``c`` a DECIMAL(10, 4) value: the placeholder gets its type.
RESPONSE_DECIMAL = {
    "numColumns": 1,
    "columns": [
        {"name": "", "dataType": {"type": "DECIMAL", "precision": 10, "scale": 4}}
    ],
}
# ``INSERT INTO t (label) VALUES (?)`` with ``label`` a VARCHAR(20) column.
RESPONSE_VARCHAR_20 = {
    "numColumns": 1,
    "columns": [
        {
            "name": "",
            "dataType": {"type": "VARCHAR", "size": 20, "characterSet": "UTF8"},
        }
    ],
}


# What the database reports in the prepare response for each placeholder
# (``parameter_data["columns"][i]["dataType"]``; ``name`` is always ``""``).
#
# Placeholders bound to a column of a table report the type of that column:
#   INSERT INTO t VALUES (?, ?, ?, ?, ?, ?)
#     DECIMAL(18,0), VARCHAR(20), VARCHAR(2000000), DECIMAL(10,4), DATE, TIMESTAMP
#   INSERT INTO t (label, id) VALUES (?, ?)      -> VARCHAR(20), DECIMAL(18,0)
#   UPDATE t SET label = ? WHERE id = ?          -> VARCHAR(20), DECIMAL(18,0)
#   SELECT * FROM t WHERE label = ? AND amount > ?
#                                                -> VARCHAR(20), DECIMAL(10,4)
#   INSERT INTO t (amount) VALUES (?)            -> DECIMAL(10,4)
#   SELECT 1 FROM (SELECT CAST(1.5 AS DECIMAL(10, 4)) AS c FROM DUAL) WHERE c = ?
#                                                -> DECIMAL(10,4); the CAST is on the
#                                                   compared value, not the placeholder
#
# Placeholders without a column to bind to report the default VARCHAR(2000000):
#   INSERT INTO t (id, label) SELECT ?, ?        -> both VARCHAR(2000000), although
#                                                   ``id`` is DECIMAL(18,0)
#   INSERT INTO t (id, label) VALUES (? + 1, CAST(? AS VARCHAR(5)))
#                                                -> both VARCHAR(2000000)
#   INSERT INTO t (amount) VALUES (CAST(? AS DECIMAL(10,4)))
#                                                -> VARCHAR(2000000), the CAST target
#                                                   type does not reach the metadata
#   INSERT INTO t (id, amount) SELECT CAST(? AS DECIMAL(18,0)), CAST(? AS DECIMAL(10,4))
#                                                -> both VARCHAR(2000000)
#   SELECT ? FROM DUAL, SELECT ? + 1 FROM DUAL, SELECT CAST(? AS DECIMAL(10,0)) ...
#                                                -> VARCHAR(2000000)
DECIMAL_18 = {"type": "DECIMAL", "precision": 18, "scale": 0}
DECIMAL_10_4 = {"type": "DECIMAL", "precision": 10, "scale": 4}
VARCHAR_20 = {"type": "VARCHAR", "size": 20, "characterSet": "UTF8"}
TABLE_BOUND = [
    (
        "INSERT INTO {t} VALUES (?, ?, ?, ?, ?, ?)",
        [
            DECIMAL_18,
            VARCHAR_20,
            UNTYPED,  # the column itself is VARCHAR(2000000)
            DECIMAL_10_4,
            {"type": "DATE", "size": 4},
            {"type": "TIMESTAMP", "withLocalTimeZone": False, "size": 16},
        ],
    ),
    ("INSERT INTO {t} (label, id) VALUES (?, ?)", [VARCHAR_20, DECIMAL_18]),
    ("UPDATE {t} SET label = ? WHERE id = ?", [VARCHAR_20, DECIMAL_18]),
    (
        "SELECT * FROM {t} WHERE label = ? AND amount > ?",
        [VARCHAR_20, DECIMAL_10_4],
    ),
    ("INSERT INTO {t} (amount) VALUES (?)", [DECIMAL_10_4]),
    (SELECT_DECIMAL, [DECIMAL_10_4]),
]
NOT_BOUND = [
    "INSERT INTO {t} (id, label) SELECT ?, ?",
    "INSERT INTO {t} (id, label) VALUES (? + 1, CAST(? AS VARCHAR(5)))",
    "INSERT INTO {t} (amount) VALUES (CAST(? AS DECIMAL(10, 4)))",
    "INSERT INTO {t} (id, amount) "
    "SELECT CAST(? AS DECIMAL(18, 0)), CAST(? AS DECIMAL(10, 4))",
    "SELECT ? FROM DUAL",
    "SELECT ? + 1 FROM DUAL",
    "SELECT CAST(? AS DECIMAL(10, 0)) FROM DUAL",
]


@pytest.fixture
def table(pyexasol_connection):
    schema = "PH_PROBE_" + uuid.uuid4().hex[:12].upper()
    pyexasol_connection.execute(f"CREATE SCHEMA {schema}")
    pyexasol_connection.execute(
        f"CREATE TABLE {schema}.t (id DECIMAL(18, 0), label VARCHAR(20), "
        "big VARCHAR(2000000), amount DECIMAL(10, 4), d DATE, ts TIMESTAMP)"
    )
    yield f"{schema}.t"
    pyexasol_connection.execute(f"DROP SCHEMA {schema} CASCADE")


def expected_response(data_types):
    """The complete parameter metadata: one unnamed column per placeholder."""
    return {
        "numColumns": len(data_types),
        "columns": [{"name": "", "dataType": data_type} for data_type in data_types],
    }


@pytest.mark.parametrize("sql, expected", TABLE_BOUND)
def test_table_bound_placeholders_report_the_column_type(prepare, table, sql, expected):
    prepare(sql.format(t=table), expected_response(expected))


@pytest.mark.parametrize("sql", NOT_BOUND)
def test_placeholders_without_column_report_the_default_varchar(prepare, table, sql):
    prepare(sql.format(t=table), expected_response([UNTYPED] * sql.count("?")))


def validate(value, data_type):
    """Map and validate a value like the WebSocket DBAPI does before sending it."""
    from pyexasol.data_types import convert_python_to_websocket
    from pyexasol.data_types.websocket_validation import validate_value_for_websocket

    mapped = convert_python_to_websocket(value, data_type)
    validate_value_for_websocket(mapped, data_type["type"])
    return mapped


def lenient_insert_mapper(value, data_type):
    """Default mapping, but ``str`` for VARCHAR(2000000), the untyped placeholder.

    This is not the nicest workaround: the prepare response of the database does not
    mark an untyped placeholder, so it is recognised only by its default type,
    VARCHAR(2000000). A real column of that type is treated the same way. It is not
    known whether there are other workarounds.

    The prepare response for such a placeholder, e.g. ``SELECT ? FROM DUAL``::

        {"numColumns": 1, "columns": [{"name": "", "dataType": {"type": "VARCHAR",
         "size": 2000000, "characterSet": "UTF8"}}]}
    """
    from pyexasol.data_types import convert_python_to_websocket

    is_untyped = data_type["type"] == "VARCHAR" and data_type["size"] == UNTYPED["size"]
    if is_untyped and value is not None and not isinstance(value, str):
        return str(value)
    return convert_python_to_websocket(value, data_type)


def test_database_reports_untyped_placeholder_as_varchar(prepare):
    prepare(SELECT_UNTYPED, RESPONSE_UNTYPED)


@pytest.mark.parametrize("value", NUMBERS)
def test_untyped_placeholder_accepts_non_str(prepare, value):
    statement, data_type = prepare(SELECT_UNTYPED, RESPONSE_UNTYPED)

    # Raises TypeError("Allowed types for VARCHAR: str, None; got ...")
    mapped = validate(value, data_type)

    statement.execute_prepared([[mapped]])
    # The database returns the untyped value as VARCHAR.
    assert statement.fetchall() == [(str(value),)]


@pytest.mark.parametrize("value", [decimal.Decimal("1.5"), 1.5])
def test_declared_decimal_placeholder_accepts_numbers(prepare, value):
    """Control: a placeholder compared with a DECIMAL column reports DECIMAL."""
    statement, data_type = prepare(SELECT_DECIMAL, RESPONSE_DECIMAL)

    statement.execute_prepared([[validate(value, data_type)]])
    assert statement.fetchall() == [(1,)]


@pytest.mark.parametrize("value", NUMBERS)
def test_mapper_can_override_untyped_placeholder(prepare, value):
    statement, data_type = prepare(SELECT_UNTYPED, RESPONSE_UNTYPED)

    mapped = lenient_insert_mapper(value, data_type)
    validate(mapped, data_type)

    statement.execute_prepared([[mapped]])
    assert statement.fetchall() == [(str(value),)]


def test_mapper_keeps_validation_for_declared_varchar(prepare, table):
    # A real VARCHAR(20) column has a different size and stays strict.
    _, data_type = prepare(
        f"INSERT INTO {table} (label) VALUES (?)", RESPONSE_VARCHAR_20
    )

    mapped = lenient_insert_mapper(15, data_type)

    with pytest.raises(TypeError, match="Allowed types for VARCHAR"):
        validate(mapped, data_type)
