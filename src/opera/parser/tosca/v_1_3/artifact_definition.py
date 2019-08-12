from opera.parser.yaml.node import Node

from ..entity import Entity
from ..map import Map
from ..path import Path
from ..reference import Reference
from ..string import String
from ..version import Version
from ..void import Void



class ArtifactDefinition(Entity):
    ATTRS = dict(
        type=Reference("artifact_types"),
        file=Path,
        repository=Reference("repositories"),
        description=String,
        deploy_path=String,
        artifact_version=Version,
        checksum=String,
        checksum_algorithm=String,
        properties=Map(Void),
    )
    REQUIRED = {"type", "file"}

    @classmethod
    def normalize(cls, yaml_node):
        if not isinstance(yaml_node.value, (str, dict)):
            cls.abort("Expected string or map.", yaml_node.loc)
        if isinstance(yaml_node.value, str):
            return Node({
                Node("type"): Node("tosca.artifacts.File"),
                Node("file"): yaml_node,
            })
        return yaml_node
