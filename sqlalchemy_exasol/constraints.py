from sqlalchemy.schema import ColumnCollectionConstraint

class DistributeByConstraint(ColumnCollectionConstraint):

   __visit_name__ = "distribute_by_constraint"
