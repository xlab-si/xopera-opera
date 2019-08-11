from ..entity import Entity
from ..list import List
from ..map import Map
from ..reference import Reference
from ..string import String
from ..void import Void


class GroupDefinition(Entity):
    ATTRS = dict(
        type=Reference("group_types"),
        description=String,
        metadata=Map(String),
        properties=Map(Void),
        members=List(Reference("topology_template", "node_templates")),
    )
    REQUIRED = {"type"}
