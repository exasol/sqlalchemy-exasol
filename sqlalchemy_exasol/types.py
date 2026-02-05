import decimal
from datetime import (
    datetime,
    time,
)

from sqlalchemy import String
from sqlalchemy.sql import sqltypes


class ExaDecimal(sqltypes.DECIMAL):
    def bind_processor(self, dialect):
        return super().bind_processor(dialect)

    def to_decimal(self, value):
        fstring = "%%.%df" % self._effective_decimal_return_scale

        if value is None:
            return None
        if isinstance(value, decimal.Decimal):
            return value
        if isinstance(value, float):
            return decimal.Decimal(fstring % value)
        return decimal.Decimal(value)

    @staticmethod
    def handle_not_as_decimal(value):
        if value is None:
            return None
        return float(value)

    def result_processor(self, dialect, coltype):
        if self.asdecimal:
            return self.to_decimal
        return self.handle_not_as_decimal


class EXATimestamp(sqltypes.TypeDecorator):
    """Coerce Python datetime to a JSON-serializable wire value for PyExasol.

    Exasol TIMESTAMP has no timezone; we format naive/UTC datetimes accordingly.
    """

    impl = sqltypes.TIMESTAMP
    cache_ok = True

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            # Normal case: a Python datetime instance
            if isinstance(value, datetime):
                # Keep microseconds; Exasol accepts 'YYYY-MM-DD HH:MM:SS.ffffff'
                return value.strftime("%Y-%m-%d %H:%M:%S.%f")
            # Defensive: if a SA DateTime *type* accidentally lands here as a value
            if isinstance(value, sqltypes.DateTime):
                return None
            return value

        return process


class EXATimestring(sqltypes.TypeDecorator):
    impl = String(16)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, time):
            # ISO 8601 time
            return value.isoformat()
        return str(value)

    def process_result_value(self, value, dialect):
        # optional: return raw string or parse back
        return value
