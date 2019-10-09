import pathlib

from opera.error import ParseError
from opera.parser.yaml.node import Node
from .string import String


class ToscaPath(String):
    @classmethod
    def build(cls, yaml_node: Node):
        path = pathlib.PurePath(yaml_node.value)
        # a deviation from the TOSCA standard
        if path.is_absolute():
            raise ParseError("Absolute paths are not supported in xOpera.", yaml_node.loc)
        return cls(path, yaml_node.loc)

    @property
    def bare(self):
        return str(self.data)
