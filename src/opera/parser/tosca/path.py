import pathlib

from .string import String


class Path(String):
    @classmethod
    def build(cls, yaml_node):
        return cls(pathlib.PurePath(yaml_node.value), yaml_node.loc)

    def canonicalize_paths(self, parent_path):
        if self.data.is_absolute():
            return

        # Next loop removes as many path/.. pairs as possible. When the path
        # is in its canonical form, it should not start with .. since that
        # would mean that something is trying to access paths outside the
        # CSAR. But during the import process, .. can be present at the
        # beggining of a path since we are processing the data in the
        # depth-first order and later canonicalizations might eliminate them.
        #
        # Examples:
        #     some/path/..  -> some
        #     ../paths/here -> ../paths/here
        #     my/../../path -> ../path

        pos = 1
        parts = list(parent_path.parts) + list(self.data.parts)

        while pos < len(parts):
            if parts[pos] == ".." and parts[pos - 1] != "..":
                del parts[pos]
                del parts[pos - 1]
                pos = max(pos - 1, 1)
            else:
                pos += 1

        self.data = pathlib.PurePath(*parts)
        return self
