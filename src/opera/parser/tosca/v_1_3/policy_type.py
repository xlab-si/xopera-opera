from ..entity import TypeEntity
from ..list import List
from ..map import Map
from ..reference import Reference, ReferenceXOR

from .property_definition import PropertyDefinition


class PolicyType(TypeEntity):
    REFERENCE = Reference("policy_types")
    ATTRS = dict(
        properties=Map(PropertyDefinition),
        targets=List(ReferenceXOR("node_types", "group_types"))
        # TODO(@tadeboro): Add triggers
    )
