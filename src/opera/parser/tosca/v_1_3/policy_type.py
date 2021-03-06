from .property_definition import PropertyDefinition
from .trigger_definition import TriggerDefinition
from ..entity import TypeEntity
from ..list import List
from ..map import Map
from ..reference import Reference, ReferenceXOR


class PolicyType(TypeEntity):
    REFERENCE = Reference("policy_types")
    ATTRS = dict(
        properties=Map(PropertyDefinition),
        targets=List(ReferenceXOR("node_types", "group_types")),
        triggers=Map(TriggerDefinition)
    )
