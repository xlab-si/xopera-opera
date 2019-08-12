import pathlib

from .string import String


class Path(String):
    @classmethod
    def build(cls, yaml_node):
        return cls(pathlib.PurePath(yaml_node.value), yaml_node.loc)
