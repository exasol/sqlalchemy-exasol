import decimal

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
