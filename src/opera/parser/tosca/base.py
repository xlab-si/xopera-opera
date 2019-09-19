from typing import Optional, NoReturn, Any

from opera.error import ParseError
from opera.parser.utils.location import Location
from opera.parser.yaml.node import Node


class Base:
    @classmethod
    def parse(cls, yaml_node: Node):
        yaml_node = cls.normalize(yaml_node)
        cls.validate(yaml_node)
        return cls.build(yaml_node)

    @classmethod
    def normalize(cls, yaml_node: Node) -> Node:
        return yaml_node

    @classmethod
    def validate(cls, _yaml_node: Node):
        pass

    @classmethod
    def build(cls, yaml_node: Node):
        return cls(yaml_node.value, yaml_node.loc)

    @classmethod
    def abort(cls, msg: str, loc: Location) -> NoReturn:
        raise ParseError("[{}] {}".format(cls.__name__, msg), loc)

    def __init__(self, data: Any, loc: Location):
        self.data = data
        self.loc = loc

    @property
    def bare(self):
        return self.data

    def __str__(self):
        return str(self.bare)

    def visit(self, method, *args, **kwargs):
        if hasattr(self, method):
            getattr(self, method)(*args, **kwargs)
