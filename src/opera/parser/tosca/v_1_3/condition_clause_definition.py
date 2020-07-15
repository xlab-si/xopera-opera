from .constraint_clause import ConstraintClause
from ..entity import Entity
from ..list import List


class ConditionClauseDefinition(Entity):
    ATTRS = dict()
    KEYNAMES = {"and", "or", "not"}

    @classmethod
    def validate(cls, yaml_node):
        for key in yaml_node.bare:
            if key in cls.KEYNAMES:
                cls.ATTRS = {
                    "and": List(ConditionClauseDefinition),
                    "or": List(ConditionClauseDefinition),
                    "not": List(ConditionClauseDefinition),
                }
            elif key == "assert":
                cls.abort("Assert keyname is deprecated. Please use and condition clause instead.", yaml_node.loc)
            else:
                if isinstance(yaml_node.bare[key], list):
                    cls.ATTRS[key] = List(ConstraintClause)
                else:
                    cls.ATTRS[key] = ConstraintClause
        super().validate(yaml_node)
