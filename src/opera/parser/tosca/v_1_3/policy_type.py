from .definition_collector_mixin import DefinitionCollectorMixin  # type: ignore
from .property_definition import PropertyDefinition
from .trigger_definition import TriggerDefinition
from ..entity import TypeEntity
from ..list import List
from ..map import Map
from ..reference import Reference, ReferenceXOR


class PolicyType(DefinitionCollectorMixin, TypeEntity):
    REFERENCE = Reference("policy_types")
    ATTRS = dict(
        properties=Map(PropertyDefinition),
        targets=List(ReferenceXOR("node_types", "group_types")),
        triggers=Map(TriggerDefinition)
    )
