import pathlib

from .string import String


class Path(String):
    @classmethod
    def build(cls, yaml_node):
        return cls(pathlib.PurePath(yaml_node.value), yaml_node.loc)

    def prefix_path(self, parent_path):
        if not self.data.is_absolute():
            self.data = parent_path / self.data
        return self
