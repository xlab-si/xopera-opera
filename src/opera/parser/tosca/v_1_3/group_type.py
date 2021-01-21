from .attribute_definition import AttributeDefinition
from .property_definition import PropertyDefinition
from ..entity import TypeEntity
from ..list import List
from ..map import Map
from ..reference import Reference


class GroupType(TypeEntity):
    REFERENCE = Reference("group_types")
    ATTRS = dict(
        attributes=Map(AttributeDefinition),
        properties=Map(PropertyDefinition),
        members=List(Reference("node_types")),
    )
