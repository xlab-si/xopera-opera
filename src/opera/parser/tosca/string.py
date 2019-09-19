from opera.parser.yaml.node import Node
from .comparable import Comparable


class String(Comparable):
    @classmethod
    def validate(cls, yaml_node: Node):
        super().validate(yaml_node)
        if not isinstance(yaml_node.value, str):
            cls.abort("Expected string input", yaml_node.loc)
