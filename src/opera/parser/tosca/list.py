from opera.error import ParseError

from .base import Base


class ListWrapper(Base):
    def __getitem__(self, index):
        return self.data[index]

    def __iter__(self):
        return iter(self.data)

    def dig(self, key, *subpath):
        try:
            item = self.data[key]
        except (IndexError, TypeError):
            return None
        return item.dig(*subpath) if subpath else item

    def visit(self, method, *args, **kwargs):
        for v in self:
            v.visit(method, *args, **kwargs)


class List:
    def __init__(self, value_class):
        self.value_class = value_class

    def parse(self, yaml_node):
        if not isinstance(yaml_node.value, list):
            raise ParseError("Expected list.", yaml_node.loc)

        return ListWrapper([
            self.value_class.parse(v) for v in yaml_node.value
        ], yaml_node.loc)
