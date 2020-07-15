from ..entity import Entity
from ..reference import ReferenceXOR
from ..string import String


class EventFilterDefinition(Entity):
    ATTRS = dict(
        node=ReferenceXOR(("topology_template", "node_templates"), "node_types"),
        requirement=String,
        capability=String,
    )
    REQUIRED = {"node"}
