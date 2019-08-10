from opera.parser.yaml.node import Node

from ..entity import Entity
from ..reference import Reference

from .range import Range


class RequirementDefinition(Entity):
    ATTRS = dict(
        capability=Reference("capability_types"),
        node=Reference("node_types"),
        relationship=Reference("relationship_types"),
        occurrences=Range,
    )
    REQUIRED = {"capability"}

    @classmethod
    def normalize(cls, yaml_node):
        if not isinstance(yaml_node.value, (str, dict)):
            cls.abort("Expected string or map.", yaml_node.loc)
        if isinstance(yaml_node.value, str):
            return Node({Node("capability"): yaml_node})
        return yaml_node
