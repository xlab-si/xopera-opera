from opera.value import Value
from opera.parser.yaml.node import Node

from .base import Base


class Void(Base):
    """
    Marker for parts of the document that should be parsed after initial
    semantic analysis.
    """

    @classmethod
    def build(cls, yaml_node):
        return cls(yaml_node)

    def __init__(self, yaml_node):
        super().__init__(yaml_node.bare, yaml_node.loc)
        self.raw = yaml_node

    def get_value(self, typ):
        return Value(typ, True, self.data)
