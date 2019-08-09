from opera.parser.yaml.node import Node

from ..entity import Entity
from ..string import String

from .credential import Credential


class RepositoryDefinition(Entity):
    ATTRS = dict(
        description=String,
        url=String,
        credential=Credential,
    )
    REQUIRED = {"url"}

    @classmethod
    def normalize(cls, yaml_node):
        if not isinstance(yaml_node.value, (str, dict)):
            cls.abort(
                "Invalid repository data. Expected string or dict.",
                yaml_node.loc,
            )
        if isinstance(yaml_node.value, str):
            return Node({Node("url"): yaml_node})
        return yaml_node
