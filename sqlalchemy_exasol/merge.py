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

    class Delete(UpdateBase):
        def __init__(self, where=None):
            self.where = where

    def __init__(self, target_table, source_expr, on):
        self.table = target_table
        self._source_expr = source_expr
        self._on = on
        self._on_columns = list(
            element
            for element in on.get_children()
            if isinstance(element, Column) and element.table == self.table
        )
        self._merge_update_values = None
        self._update_where = None
        self._merge_insert_values = None
        self._insert_where = None
        self._merge_delete = False
        self._delete_where = None
        self._delete = None

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
                for column in self.table.c
                if column not in self._on_columns and column.name in src_columns
            )
            [values.update({column: src_columns[column.name]}) for column in columns]
        self._merge_update_values = ValuesBase(self.table, values, [])
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
            columns = (column for column in self.table.c if column.name in src_columns)
            [values.update({column: src_columns[column.name]}) for column in columns]
        self._merge_insert_values = ValuesBase(self.table, values, [])
        if where is not None:
            self._insert_where = Merge._append_where(self._insert_where, where)

    @_generative
    def delete(self, where=None):
        self._merge_delete = True
        self.delete_clause = Merge.Delete(where)

    @staticmethod
    def _append_where(where, addition):
        if where is None:
            return addition
        return and_(where, addition)

    def _is_merge_update(self):
        return self._merge_update_values is not None

    def _is_merge_delete(self):
        return not self._is_merge_update() and self._merge_delete

    def _is_merge_insert(self):
        return self._merge_insert_values is not None

    def _compile_update(self, compiler):
        columns = crud._get_crud_params(compiler, self._merge_update_values)
        sql = ""
        sql += "\nWHEN MATCHED THEN UPDATE SET "
        sql += ", ".join(compiler.visit_column(c[0]) + "=" + c[1] for c in columns)
        if self._merge_delete:
            sql += "\nDELETE "
            if self._delete_where is not None:
                sql += " WHERE %s" % compiler.process(self._delete_where)
        else:
            if self._update_where is not None:
                sql += " WHERE %s" % compiler.process(self._update_where)
        return sql

    def _compile_insert(self, compiler):
        columns = crud._get_crud_params(compiler, self._merge_insert_values)
        sql = "\nWHEN NOT MATCHED THEN INSERT "
        sql += "(%s) " % ", ".join(compiler.visit_column(c[0]) for c in columns)
        sql += "VALUES (%s) " % ", ".join(c[1] for c in columns)
        if self._insert_where is not None:
            sql += "WHERE %s" % compiler.process(self._insert_where)
        return sql

    def visit(self, compiler):
        sql = "MERGE INTO %s " % compiler.process(self.table, asfrom=True)
        sql += "USING %s " % compiler.process(self._source_expr, asfrom=True)
        sql += "ON ( %s ) " % compiler.process(self._on)
        if self._is_merge_update():
            sql += self._compile_update(compiler)
        if self._is_merge_delete():
            sql += compiler.process(self.delete_clause)
        if self._is_merge_insert():
            sql += self._compile_insert(compiler)
        return sql


def merge(target_table, source_expr, on):
    return Merge(target_table, source_expr, on)


@compiles(Merge, "exasol")
def visit_merge(node, compiler, **_):
    return node.visit(compiler)


@compiles(Merge.Delete, "exasol")
def visit_merge_delete(node, compiler, **_):
    sql = "\nWHEN MATCHED THEN DELETE "
    if node.where is not None:
        sql += "WHERE %s" % compiler.process(node.where)
    return sql
