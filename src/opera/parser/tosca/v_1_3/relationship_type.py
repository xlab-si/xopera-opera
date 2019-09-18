from .attribute_definition import AttributeDefinition
from .interface_definition_for_type import InterfaceDefinitionForType
from .property_definition import PropertyDefinition
from ..entity import TypeEntity
from ..list import List
from ..map import Map
from ..reference import Reference


class RelationshipType(TypeEntity):
    REFERENCE = Reference("relationship_types")
    ATTRS = dict(
        properties=Map(PropertyDefinition),
        attributes=Map(AttributeDefinition),
        interfaces=Map(InterfaceDefinitionForType),
        valid_target_types=List(Reference("capability_types")),
    )
