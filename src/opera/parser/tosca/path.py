import pathlib

from opera.parser.yaml.node import Node
from .string import String


class ToscaPath(String):
    @classmethod
    def build(cls, yaml_node: Node):
        return cls(pathlib.PurePath(yaml_node.value), yaml_node.loc)

    @property
    def bare(self):
        return str(self.data)
