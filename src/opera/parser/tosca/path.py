import pathlib

from .string import String


class Path(String):
    @classmethod
    def build(cls, yaml_node):
        return cls(pathlib.PurePath(yaml_node.value), yaml_node.loc)

    def prefix_path(self, parent_path):
        if not self.data.is_absolute():
            self.data = parent_path / self.data

    def resolve_path(self, base_path):
        # Absolute path is relative to the CSAR root folder, so we need to
        # strip the root off of it.
        if self.data.is_absolute():
            path = self.data.relative_to(self.data.root)
        else:
            path = self.data
        self.data = self._compact_path(path)
        self._validate_path(base_path)

    @staticmethod
    def _compact_path(path):
        # Next loop removes as many path/.. pairs as possible. When the path
        # is in its canonical form, it should not start with .. since that
        # would mean that something is trying to access paths outside the
        # CSAR.
        #
        # Examples:
        #     some/path/..  -> some
        #     ../paths/here -> ../paths/here
        #     my/../../path -> ../path

        pos = 1
        parts = list(path.parts)

        while pos < len(parts):
            if parts[pos] == ".." and parts[pos - 1] != "..":
                del parts[pos]
                del parts[pos - 1]
                pos = max(pos - 1, 1)
            else:
                pos += 1

        return pathlib.PurePath(*parts)

    def _validate_path(self, base_path):
        # Abstract checks
        if str(self.data) == ".":
            self.abort("Path points to the CSAR root.", self.loc)
        if self.data.parts[0] == "..":
            self.abort("Path points outside the CSAR.", self.loc)

        # Concrete checks
        abs_path = base_path / self.data
        if not abs_path.exists():
            self.abort("Path {} does not exist.".format(abs_path), self.loc)
        # We test for symlinks separately since is_dir() and is_file() return
        # True on symlinks and this is not what we want.
        if abs_path.is_symlink():
            self.abort("Path {} is a symlink.".format(abs_path), self.loc)
        if not abs_path.is_dir() and not abs_path.is_file():
            self.abort(
                "Path {} is not file or folder.".format(abs_path), self.loc,
            )
