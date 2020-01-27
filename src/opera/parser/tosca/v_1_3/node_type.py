from ..entity import TypeEntity
from ..map import Map, OrderedMap
from ..reference import Reference
from ..string import String

from .artifact_definition import ArtifactDefinition
from .attribute_definition import AttributeDefinition
from .capability_definition import CapabilityDefinition
from .definition_collector_mixin import DefinitionCollectorMixin
from .interface_definition_for_type import InterfaceDefinitionForType
from .property_definition import PropertyDefinition
from .requirement_definition import RequirementDefinition


class NodeType(DefinitionCollectorMixin, TypeEntity):
    REFERENCE = Reference("node_types")
    ATTRS = dict(
        attributes=Map(AttributeDefinition),
        properties=Map(PropertyDefinition),
        requirements=OrderedMap(RequirementDefinition),
        capabilities=Map(CapabilityDefinition),
        interfaces=Map(InterfaceDefinitionForType),
        artifacts=Map(ArtifactDefinition),
    )
