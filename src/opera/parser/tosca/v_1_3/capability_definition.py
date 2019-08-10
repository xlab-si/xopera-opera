from opera.parser.yaml.node import Node

from ..entity import Entity
from ..reference import Reference
from ..map import Map
from ..list import List
from ..string import String
from ..void import Void

from .attribute_definition import AttributeDefinition
from .property_definition import PropertyDefinition
from .range import Range


class CapabilityDefinition(Entity):
    ATTRS = dict(
        type=Reference("capability_types"),
        description=String,
        properties=Map(PropertyDefinition),
        attributes=Map(AttributeDefinition),
        valid_source_types=List(Reference("node_types")),
        occurrences=Range,
    )
    REQUIRED = {"type"}

    @classmethod
    def normalize(cls, yaml_node):
        if not isinstance(yaml_node.value, (str, dict)):
            cls.abort("Expected string or map.", yaml_node.loc)
        if isinstance(yaml_node.value, str):
            return Node({Node("type"): yaml_node})
        return yaml_node
