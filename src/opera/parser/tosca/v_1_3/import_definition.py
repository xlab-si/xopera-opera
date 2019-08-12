from opera.parser.yaml.node import Node

from ..entity import Entity
from ..path import Path
from ..string import String


class ImportDefinition(Entity):
    ATTRS = dict(
        file=Path,
        repository=String,
        namespace_prefix=String,
        namespace_uri=String,
    )
    DEPRECATED = {
        "namespace_uri",
    }

    @classmethod
    def normalize(cls, yaml_node):
        if not isinstance(yaml_node.value, (str, dict)):
            cls.abort(
                "Invalid import data. Expected string or dict.", yaml_node.loc,
            )
        if isinstance(yaml_node.value, str):
            return Node({Node("file"): yaml_node})
        return yaml_node
