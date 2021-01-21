from .attribute_definition import AttributeDefinition
from .property_definition import PropertyDefinition
from ..entity import TypeEntity
from ..list import List
from ..map import Map
from ..reference import Reference


class CapabilityType(TypeEntity):
    REFERENCE = Reference("capability_types")
    ATTRS = dict(
        properties=Map(PropertyDefinition),
        attributes=Map(AttributeDefinition),
        valid_source_types=List(Reference("node_types")),
    )
