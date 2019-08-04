import re

from yaml.nodes import MappingNode, ScalarNode, SequenceNode


class Resolver:
    defaults = {
        ScalarNode: "tag:yaml.org,2002:str",
        SequenceNode: "tag:yaml.org,2002:seq",
        MappingNode: "tag:yaml.org,2002:map",
    }
    resolvers = {}

    @classmethod
    def add_implicit_resolver(cls, tag, regex, first):
        for ch in first:
            cls.resolvers.setdefault(ch, []).append((tag, regex))

    def resolve(self, kind, value, implicit):
        if kind is ScalarNode and implicit[0]:
            first_ch = value and value[0]
            for tag, regex in self.resolvers.get(first_ch, []):
                if regex.match(value):
                    return tag
        return self.defaults[kind]

    def descend_resolver(_self, _current_node, _current_index):
        pass

    def ascend_resolver(_self):
        pass


# From https://yaml.org/spec/1.2/spec.html#id2804923
Resolver.add_implicit_resolver(
    "tag:yaml.org,2002:null",
    re.compile(r"^(~|null|Null|NULL|)$"),
    ["~", "n", "N", ""],
)

Resolver.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(true|True|TRUE|false|False|FALSE)$"),
    list("tTfF"),
)

Resolver.add_implicit_resolver(
    "tag:yaml.org,2002:int",
    re.compile(r"^([-+]?[0-9]+|0o[0-7]+|0x[0-9a-fA-F]+)$"),
    list("-+0123456789"),
)

Resolver.add_implicit_resolver(
    "tag:yaml.org,2002:float",
    re.compile(
        r"""^(
            [-+]?(\.[0-9]+|[0-9]+(\.[0-9]*)?)([eE][-+]?[0-9]+)?
          | [-+]?\.(inf|Inf|INF)
          | \.(nan|NaN|NAN)
        )$""", re.X),
    list("-+0123456789."),
)
