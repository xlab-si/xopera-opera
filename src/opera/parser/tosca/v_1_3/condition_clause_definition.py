from typing import Dict, Type, Union

from .constraint_clause import ConstraintClause
from ..base import Base
from ..entity import Entity
from ..list import List
from ..map import Map
from ..reference import Reference, ReferenceXOR


class ConditionClauseDefinition(Entity):
    ATTRS: Dict[str, Union[Type[Base], Base, Map, List, Reference, ReferenceXOR]] = dict()
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
