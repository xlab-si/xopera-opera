from .property_definition import PropertyDefinition
from ..entity import TypeEntity
from ..map import Map
from ..reference import Reference


class PolicyType(TypeEntity):
    REFERENCE = Reference("policy_types")
    ATTRS = dict(
        properties=Map(PropertyDefinition),
        # TODOD(@tadeboro): Add targets, triggers
    )
