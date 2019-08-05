from yaml.constructor import BaseConstructor, ConstructorError

from opera.parser.utils.location import Location

from .node import Node


class Constructor(BaseConstructor):
    def __init__(self, stream_name):
        super().__init__()
        self._stream_name = stream_name

    def _pos(self, node):
        # Convert 0-based indices to 1-based (text editor) marks
        return Location(
            self._stream_name,
            node.start_mark.line + 1,
            node.start_mark.column + 1,
        )

    def construct_yaml_null(self, node):
        self.construct_scalar(node)
        return Node(None, self._pos(node))

    def construct_yaml_bool(self, node):
        value = self.construct_scalar(node).lower()
        return Node(value == "true", self._pos(node))

    def construct_yaml_int(self, node):
        value = self.construct_scalar(node)
        if value.startswith("0o"):
            base = 8
        elif value.startswith("0x"):
            base = 16
        else:
            base = 10
        return Node(int(value, base=base), self._pos(node))

    def construct_yaml_float(self, node):
        value = self.construct_scalar(node).lower()
        if value == ".nan":
            value = "nan"
        elif value.endswith(".inf"):
            value = value.replace(".", "")
        return Node(float(value), self._pos(node))

    def construct_yaml_str(self, node):
        return Node(self.construct_scalar(node), self._pos(node))

    def construct_yaml_seq(self, node):
        data = Node([], self._pos(node))
        yield data
        data.value.extend(self.construct_sequence(node))

    def construct_yaml_map(self, node):
        data = Node({}, self._pos(node))
        yield data
        data.value.update(self.construct_mapping(node))

    def construct_undefined(self, node):
        raise ConstructorError(
            None, None,
            "could not determine a constructor for {}".format(node.tag),
            node.start_mark,
        )


# Add constructors for YAML 1.2 types (core schema).
for tag in ("null", "bool", "int", "float", "str", "seq", "map"):
    Constructor.add_constructor(
        "tag:yaml.org,2002:{}".format(tag),
        getattr(Constructor, "construct_yaml_{}".format(tag)),
    )

# Error reporter.
Constructor.add_constructor(None, Constructor.construct_undefined)
