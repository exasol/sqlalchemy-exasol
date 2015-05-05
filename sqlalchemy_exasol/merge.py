from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ClauseElement, Executable, ValuesBase, \
    and_, UpdateBase
from sqlalchemy.sql.base import _generative
from sqlalchemy.sql import crud
from sqlalchemy.schema import Column


class Merge(UpdateBase):

    __visit_name__ = 'merge'

    def __init__(self,
                 target_table,
                 source_expr,
                 on):
        self._target_table = target_table
        self._source_expr = source_expr
        self._on = on
        self._on_columns = []
        elements_to_check = list(on.get_children())
        for e in elements_to_check:
            if isinstance(e, Column):
                if  e.table == self._target_table:
                    self._on_columns.append(e)
            else:
                elements_to_check.extend(e.get_children())
        self._merge_update_values = None
        self._update_where = None
        self._merge_insert_values = None
        self._insert_where = None
        self._merge_delete = False
        self._delete_where = None

    def _get_source_cols(self):
        source_cols = {}
        elements_to_check = list(self._source_expr.get_children())
        for e in elements_to_check:
            if isinstance(e, Column):
                source_cols[e.name] = e
        return source_cols

    @_generative
    def update(self, values=None, where=None):
        # by default update all columns of target table that are
        # present in the source expression but exclude columns part
        # of the MERGE ON condition
        if values is None:
            source_cols = self._get_source_cols()
            values = {}
            for c in self._target_table.c:
                if c not in self._on_columns and c.name in source_cols:
                    values[c] = source_cols[c.name]
        self._merge_update_values = ValuesBase(self._target_table, values, [])
        if where is not None:
            if self._merge_delete:
                self._delete_where = self._append_where(self._delete_where, where)
            else: 
                self._update_where = self._append_where(self._update_where, where)

    @_generative
    def insert(self, values=None, where=None):
        # by default set all columns of target table that are
        # present in the source expression but exclude columns part
        # of the MERGE ON condition
        if values is None:
            source_cols = self._get_source_cols()
            values = {}
            for c in self._target_table.c:
                if c.name in source_cols:
                    values[c] = source_cols[c.name]
        self._merge_insert_values = ValuesBase(self._target_table, values, [])
        if where is not None:
            self._insert_where = self._append_where(self._insert_where, where)

    @_generative
    def delete(self, where=None):
        self._merge_delete = True
        if self._merge_update_values is None and where is not None:
            self._delete_where = self._append_where(self._delete_where, where)

    def _append_where(self, where, addition):
        if where is not None:
            where = and_(where, addition)
        else:
            where = addition
        return where

def merge(target_table, source_expr, on):
    return Merge(target_table, source_expr, on)


@compiles(Merge, 'exasol')
def visit_merge(element, compiler, **kw):
    msql = "MERGE INTO %s " % compiler.process(element._target_table,
                                              asfrom=True)
    msql += "USING %s " % compiler.process(element._source_expr,
                                           asfrom=True)
    msql += "ON ( %s ) " % compiler.process(element._on)

    if element._merge_update_values is not None:
        cols = crud._get_crud_params(compiler, element._merge_update_values)
        msql += "\nWHEN MATCHED THEN UPDATE SET "
        msql += ', '.join(compiler.visit_column(c[0]) + '=' + c[1] for c in cols)
        if element._merge_delete:
            msql += "\nDELETE "
            if element._delete_where is not None:
                msql += " WHERE %s" % compiler.process(element._delete_where)
        else:
            if element._update_where is not None:
                msql += " WHERE %s" % compiler.process(element._update_where)
    else:
        if element._merge_delete:
            msql += "\nWHEN MATCHED THEN DELETE "
            if element._delete_where is not None:
                msql += "WHERE %s" % compiler.process(element._delete_where)
    if element._merge_insert_values is not None:
        cols = crud._get_crud_params(compiler, element._merge_insert_values)
        msql += "\nWHEN NOT MATCHED THEN INSERT "
        msql += "(%s) " % ', '.join(compiler.visit_column(c[0]) for c in cols)
        msql += "VALUES (%s) " % ', '.join(c[1] for c in cols)
        if element._insert_where is not None:
            msql += "WHERE %s" % compiler.process(element._insert_where)

    return msql
