from ..entity import TypeEntity
from ..list import List
from ..map import Map
from ..reference import Reference
from ..string import String

from .attribute_definition import AttributeDefinition
from .definition_collector_mixin import DefinitionCollectorMixin
from .interface_definition_for_type import InterfaceDefinitionForType
from .property_definition import PropertyDefinition


class RelationshipType(DefinitionCollectorMixin, TypeEntity):
    REFERENCE = Reference("relationship_types")
    ATTRS = dict(
        properties=Map(PropertyDefinition),
        attributes=Map(AttributeDefinition),
        interfaces=Map(InterfaceDefinitionForType),
        valid_target_types=List(Reference("capability_types")),
    )
