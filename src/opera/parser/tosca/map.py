import collections

from opera.error import ParseError
from opera.parser.yaml.node import Node

from .base import Base


class MapWrapper(Base):
    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def values(self):
        return self.data.values()

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def get(self, key, default=None):
        return self.data.get(key, default)

    def dig(self, key, *subpath):
        if key not in self.data:
            return None
        if not subpath:
            return self.data[key]
        return self.data[key].dig(*subpath)

    def merge(self, other):
        duplicates = set(self.keys()) & set(other.keys())
        if duplicates:
            self.abort(
                "Duplicate keys '{}' found in {} and {}".format(
                    ", ".join(duplicates), self.loc, other.loc,
                ), self.loc,
            )
        self.data.update(other.data)

    def visit(self, method, *args, **kwargs):
        for v in self.values():
            v.visit(method, *args, **kwargs)


class Map:
    def __init__(self, value_class):
        self.value_class = value_class

    def parse(self, yaml_node):
        if not isinstance(yaml_node.value, dict):
            raise ParseError("Expected map.", yaml_node.loc)

        for k in yaml_node.value:
            if not isinstance(k.value, str):
                cls.abort("Expected string key.", k.loc)

        return MapWrapper(collections.OrderedDict(
            (k.value, self.value_class.parse(v))
            for k, v in yaml_node.value.items()
        ), yaml_node.loc)


class OrderedMap(Map):
    def parse(self, yaml_node):
        if not isinstance(yaml_node.value, list):
            raise ParseError(
                "Expected list of single-key maps.", yaml_node.loc,
            )

        data = collections.OrderedDict()
        for item in yaml_node.value:
            if not isinstance(item.value, dict) or len(item.value) != 1:
                raise ParseError("Expected single-key map.", item.loc)
            (k, v), = item.value.items()
            data[k] = v
        return super().parse(Node(data, yaml_node.loc))
