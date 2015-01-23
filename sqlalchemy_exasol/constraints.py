from sqlalchemy.schme import ColmunCollectionConstraint

class DistributeByConstraint(ColumnCollectionConstraint):

   __visit_name__ = "distribute_by_constraint"
