from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import Column
from sqlalchemy.sql import crud
from sqlalchemy.sql.base import _generative
from sqlalchemy.sql.expression import (
    ColumnClause,
    UpdateBase,
    ValuesBase,
    and_,
)


class Merge(UpdateBase):
    __visit_name__ = "merge"

    def __init__(self, target_table, source_expr, on):
        self._target_table = target_table
        self._source_expr = source_expr
        self._on = on
        self._on_columns = list(
            element
            for element in on.get_children()
            if isinstance(element, Column) and element.table == self._target_table
        )
        self._merge_update_values = None
        self._update_where = None
        self._merge_insert_values = None
        self._insert_where = None
        self._merge_delete = False
        self._delete_where = None

    def _source_columns(self):
        elements = list(
            element
            for element in self._source_expr.get_children()
            if isinstance(element, ColumnClause)
        )
        return {element.name: element for element in elements}

    @_generative
    def update(self, values=None, where=None):
        # by default update all columns of target table that are
        # present in the source expression but exclude columns part
        # of the MERGE ON condition
        if values is None:
            values = {}
            src_columns = self._source_columns()
            columns = (
                column
                for column in self._target_table.c
                if column not in self._on_columns and column.name in src_columns
            )
            [values.update({column: src_columns[column.name]}) for column in columns]
        self._merge_update_values = ValuesBase(self._target_table, values, [])
        if where is not None:
            if self._merge_delete:
                self._delete_where = Merge._append_where(self._delete_where, where)
            else:
                self._update_where = Merge._append_where(self._update_where, where)

    @_generative
    def insert(self, values=None, where=None):
        # by default set all columns of target table that are
        # present in the source expression but exclude columns part
        # of the MERGE ON condition
        if values is None:
            values = {}
            src_columns = self._source_columns()
            columns = (
                column for column in self._target_table.c if column.name in src_columns
            )
            [values.update({column: src_columns[column.name]}) for column in columns]
        self._merge_insert_values = ValuesBase(self._target_table, values, [])
        if where is not None:
            self._insert_where = Merge._append_where(self._insert_where, where)

    @_generative
    def delete(self, where=None):
        self._merge_delete = True
        if self._merge_update_values is None and where is not None:
            self._delete_where = Merge._append_where(self._delete_where, where)

    @staticmethod
    def _append_where(where, addition):
        if where is None:
            return addition
        return and_(where, addition)

    @property
    def is_merge_update(self):
        return self._merge_update_values is not None

    @property
    def is_merge_delete(self):
        return not self.is_merge_update and self._merge_delete

    @property
    def is_merge_insert(self):
        return self._merge_insert_values is not None

    def visit(self, compiler, **kw):
        msql = "MERGE INTO %s " % compiler.process(self._target_table, asfrom=True)
        msql += "USING %s " % compiler.process(self._source_expr, asfrom=True)
        msql += "ON ( %s ) " % compiler.process(self._on)

        if self.is_merge_update:
            columns = crud._get_crud_params(compiler, self._merge_update_values)
            msql += "\nWHEN MATCHED THEN UPDATE SET "
            msql += ", ".join(compiler.visit_column(c[0]) + "=" + c[1] for c in columns)
            if self._merge_delete:
                msql += "\nDELETE "
                if self._delete_where is not None:
                    msql += " WHERE %s" % compiler.process(self._delete_where)
            else:
                if self._update_where is not None:
                    msql += " WHERE %s" % compiler.process(self._update_where)

        if self.is_merge_delete:
            msql += "\nWHEN MATCHED THEN DELETE "
            if self._delete_where is not None:
                msql += "WHERE %s" % compiler.process(self._delete_where)

        if self.is_merge_insert:
            columns = crud._get_crud_params(compiler, self._merge_insert_values)
            msql += "\nWHEN NOT MATCHED THEN INSERT "
            msql += "(%s) " % ", ".join(compiler.visit_column(c[0]) for c in columns)
            msql += "VALUES (%s) " % ", ".join(c[1] for c in columns)
            if self._insert_where is not None:
                msql += "WHERE %s" % compiler.process(self._insert_where)

        return msql


def merge(target_table, source_expr, on):
    return Merge(target_table, source_expr, on)


@compiles(Merge, "exasol")
def visit_merge(merge_node, compiler, **kw):
    return merge_node.visit(compiler, **kw)
