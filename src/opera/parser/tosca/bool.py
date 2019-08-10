from .comparable import Comparable


class Bool(Comparable):
    @classmethod
    def validate(cls, yaml_node):
        super().validate(yaml_node)
        if not isinstance(yaml_node.value, bool):
            cls.abort("Expected boolean value.", yaml_node.loc)
