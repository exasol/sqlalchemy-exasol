import decimal

from sqlalchemy.sql import sqltypes


class ExaDecimal(sqltypes.DECIMAL):
    def bind_processor(self, dialect):
        return super().bind_processor(dialect)

    def result_processor(self, dialect, coltype):
        if not self.asdecimal:
            return lambda value: None if value is None else float(value)

        fstring = "%%.%df" % self._effective_decimal_return_scale

        def to_decimal(value):
            if value is None:
                return None
            if isinstance(value, decimal.Decimal):
                return value
            if isinstance(value, float):
                return decimal.Decimal(fstring % value)
            return decimal.Decimal(value)

        return to_decimal
