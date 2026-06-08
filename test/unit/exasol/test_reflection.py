import pytest
from sqlalchemy import exc as sa_exc
from sqlalchemy import types as sqltypes

from sqlalchemy_exasol import base


def _make_column_metadata(**overrides):
    row = {
        "colname": "name",
        "coltype": "VARCHAR",
        "length": 20,
        "precision": 0,
        "scale": 0,
        "nullable": True,
        "default": None,
        "identity": None,
        "is_distribution_key": False,
    }
    row.update(overrides)
    return base.ColumnMetadata(**row)


@pytest.mark.parametrize(
    ("column_metadata", "expected_type", "expected_attributes"),
    [
        pytest.param(
            _make_column_metadata(),
            sqltypes.VARCHAR,
            {"length": 20},
            id="varchar",
        ),
        pytest.param(
            _make_column_metadata(coltype="CHAR UTF8", length=8),
            sqltypes.CHAR,
            {"length": 8},
            id="char-with-charset-and-space",
        ),
        pytest.param(
            _make_column_metadata(
                coltype="DECIMAL", length=None, precision=18, scale=0
            ),
            sqltypes.INTEGER,
            {},
            id="decimal18-becomes-integer",
        ),
        pytest.param(
            _make_column_metadata(
                coltype="DECIMAL", length=None, precision=36, scale=0
            ),
            sqltypes.DECIMAL,
            {"precision": 36, "scale": 0},
            id="decimal36-stays-decimal",
        ),
        pytest.param(
            _make_column_metadata(
                coltype="DECIMAL", length=None, precision=10, scale=2
            ),
            sqltypes.DECIMAL,
            {"precision": 10, "scale": 2},
            id="decimal-keeps-precision-and-scale",
        ),
    ],
)
def test_get_coltype_maps_to_expected_sqlalchemy_types(
    column_metadata, expected_type, expected_attributes
):
    dialect = base.EXADialect()
    actual = dialect._get_coltype(column_metadata)

    assert isinstance(actual, expected_type)
    for attribute_name, expected_value in expected_attributes.items():
        assert getattr(actual, attribute_name) == expected_value


def test_get_coltype_warns_and_falls_back_to_nulltype_for_unknown_types():
    dialect = base.EXADialect()
    column_metadata = _make_column_metadata(
        coltype="NOT_A_REAL_TYPE",
        length=None,
        precision=None,
        scale=None,
    )

    with pytest.warns(
        sa_exc.SAWarning,
        match=(
            f"Did not recognize type '{column_metadata.coltype}' "
            f"of column '{column_metadata.colname}'"
        ),
    ):
        actual = dialect._get_coltype(column_metadata)

    assert isinstance(actual, sqltypes.NullType)
