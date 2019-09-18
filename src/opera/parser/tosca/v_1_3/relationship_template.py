from .interface_definition_for_template import InterfaceDefinitionForTemplate
from ..entity import Entity
from ..map import Map
from ..reference import Reference
from ..string import String
from ..void import Void


class RelationshipTemplate(Entity):
    ATTRS = dict(
        type=Reference("relationship_types"),
        description=String,
        metadata=Map(String),
        properties=Map(Void),
        attributes=Map(Void),
        interfaces=Map(InterfaceDefinitionForTemplate),
        copy=Reference("topology_template", "relationship_templates"),
    )
    REQUIRED = {"type"}
