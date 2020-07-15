import re

from .string import String

TIMESTAMP_CANONICAL_RE = re.compile(
    r"""
    [0-9][0-9][0-9][0-9]
    -[0-9][0-9]
    -[0-9][0-9]
    T[0-9][0-9]
    :[0-9][0-9]
    :[0-9][0-9]
    (\.[0-9]*[1-9])?
    Z
    """,
    re.ASCII | re.VERBOSE,
)

TIMESTAMP_RE = re.compile(
    r"""
     [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]
    |[0-9][0-9][0-9][0-9]
     -[0-9][0-9]?
     -[0-9][0-9]?
     ([Tt]|[ \t]+)[0-9][0-9]?
     :[0-9][0-9]
     :[0-9][0-9]
     (\.[0-9]*)?
     (([ \t]*)Z|[-+][0-9][0-9]?(:[0-9][0-9])?)?
    """,
    re.ASCII | re.VERBOSE,
)


class Timestamp(String):
    @classmethod
    def validate(cls, yaml_node):
        super().validate(yaml_node)
        if not TIMESTAMP_CANONICAL_RE.fullmatch(yaml_node.value) and not TIMESTAMP_RE.fullmatch(yaml_node.value):
            cls.abort("Invalid timestamp format.", yaml_node.loc)
