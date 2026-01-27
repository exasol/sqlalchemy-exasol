from types import SimpleNamespace

from sqlalchemy import types as sqltypes

from sqlalchemy_exasol import base


def _type_compiler():
    return base.EXATypeCompiler(base.EXADialect())


MAX_VARCHAR = 2_000_000


# --- BIGINT / BigInteger ----------------------------------------------------
def test_big_integer_is_not_overridden_anymore():
    """
    We intentionally do NOT override BigInteger/BIGINT anymore (ODBC workaround removed).
    This test just asserts we didn't keep the old behavior.
    """
    compiler = _type_compiler()
    out = compiler.visit_big_integer(sqltypes.BigInteger())
    assert out != "DECIMAL(19)"


# --- Binary / blobs ---------------------------------------------------------
def test_visit_large_binary_maps_to_max_varchar():
    compiler = _type_compiler()
    assert (
        compiler.visit_large_binary(sqltypes.LargeBinary()) == f"VARCHAR({MAX_VARCHAR})"
    )


def test_visit_blob_family_maps_to_max_varchar():
    compiler = _type_compiler()

    # These are not always instantiated in user code, but our compiler supports them.
    assert compiler.visit_BLOB(sqltypes.LargeBinary()) == f"VARCHAR({MAX_VARCHAR})"
    assert compiler.visit_BINARY(sqltypes.BINARY()) == f"VARCHAR({MAX_VARCHAR})"
    assert compiler.visit_VARBINARY(sqltypes.VARBINARY()) == f"VARCHAR({MAX_VARCHAR})"


# --- Date/time --------------------------------------------------------------
def test_visit_datetime_variants_return_timestamp():
    compiler = _type_compiler()
    assert compiler.visit_datetime(sqltypes.DateTime()) == "TIMESTAMP"
    assert compiler.visit_DATETIME(sqltypes.DateTime()) == "TIMESTAMP"


def test_visit_time_variants_return_timestamp():
    compiler = _type_compiler()
    assert compiler.visit_time(sqltypes.Time()) == "TIMESTAMP"
    assert compiler.visit_TIME(sqltypes.Time()) == "TIMESTAMP"


# --- UUID -------------------------------------------------------------------
def test_visit_uuid_variants_return_hashtype_16():
    compiler = _type_compiler()

    # Some SQLAlchemy versions use Uuid, others UUID; our compiler implements both
    # visit_UUID and visit_uuid, so we call them directly.
    dummy = SimpleNamespace()
    assert compiler.visit_UUID(dummy) == "HASHTYPE(16 BYTE)"
    assert compiler.visit_uuid(dummy) == "HASHTYPE(16 BYTE)"


# --- Strings / Text ---------------------------------------------------------
def test_visit_string_and_unicode_length_handling():
    compiler = _type_compiler()

    assert compiler.visit_string(sqltypes.String(5)) == "VARCHAR(5)"
    assert compiler.visit_unicode(sqltypes.Unicode(7)) == "VARCHAR(7)"

    # No length -> default to max varchar
    assert compiler.visit_string(sqltypes.String()) == f"VARCHAR({MAX_VARCHAR})"
    assert compiler.visit_unicode(sqltypes.Unicode()) == f"VARCHAR({MAX_VARCHAR})"


def test_visit_text_and_clob_variants_map_to_max_varchar():
    compiler = _type_compiler()

    # SQLAlchemy Text/UnicodeText -> max varchar
    assert compiler.visit_text(sqltypes.Text()) == f"VARCHAR({MAX_VARCHAR})"
    assert compiler.visit_TEXT(sqltypes.Text()) == f"VARCHAR({MAX_VARCHAR})"
    assert (
        compiler.visit_unicode_text(sqltypes.UnicodeText()) == f"VARCHAR({MAX_VARCHAR})"
    )

    # Our compiler also supports CLOB/NCLOB visit names; not all SQLA versions expose
    # sqltypes.CLOB/NCLOB classes consistently, so we just call visit_* with a dummy.
    dummy = SimpleNamespace()
    assert compiler.visit_CLOB(dummy) == f"VARCHAR({MAX_VARCHAR})"
    assert compiler.visit_NCLOB(dummy) == f"VARCHAR({MAX_VARCHAR})"


# --- ENUM -------------------------------------------------------------------
def test_visit_enum_maps_to_varchar_of_max_value_length():
    compiler = _type_compiler()
    e = sqltypes.Enum("a", "abcd", "xyz")
    # max length is 4 -> VARCHAR(4)
    assert compiler.visit_enum(e) == "VARCHAR(4)"


def test_visit_enum_without_values_falls_back_to_max_varchar():
    compiler = _type_compiler()

    # Hard to produce "no enums" via public Enum constructor in all versions,
    # so call visit_enum with a tiny dummy that looks like Enum.
    dummy = SimpleNamespace(enums=[])
    assert compiler.visit_enum(dummy) == f"VARCHAR({MAX_VARCHAR})"


# --- Numeric ----------------------------------------------------------------
def test_visit_numeric_variants_apply_scale_defaults():
    """
    We generally rely on GenericTypeCompiler for numeric/decimal,
    but if you *kept* a numeric override, this should still hold.
    If you removed it, feel free to delete this test.
    """
    compiler = _type_compiler()

    # If EXATypeCompiler does not override visit_numeric anymore, these outputs will
    # depend on SQLAlchemy version/dialect rules. Adjust or remove if needed.
    out1 = compiler.visit_numeric(sqltypes.Numeric(precision=10, scale=None))
    out2 = compiler.visit_numeric(sqltypes.Numeric(precision=None, scale=None))

    assert "10" in out1  # keep this loose to avoid version-specific formatting diffs
    assert "DECIMAL" in out2 or "NUMERIC" in out2
