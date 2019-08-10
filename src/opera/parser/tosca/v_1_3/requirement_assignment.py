from opera.parser.yaml.node import Node

from ..entity import Entity
from ..reference import Reference
from ..string import String
from ..void import Void

from .node_filter_definition import NodeFilterDefinition
from .range import Range


class RequirementAssignment(Entity):
    ATTRS = dict(
        capability=String,
        node=Reference("topology_template", "node_templates"),
        relationship=Reference("topology_template", "relationship_templates"),
        node_filter=NodeFilterDefinition,
        occurrences=Range,
    )

    @classmethod
    def normalize(cls, yaml_node):
        if not isinstance(yaml_node.value, (str, dict)):
            cls.abort("Expected string or map.", yaml_node.loc)
        if isinstance(yaml_node.value, str):
            return Node({Node("node"): yaml_node})
        return yaml_node
