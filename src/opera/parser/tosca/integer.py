from .comparable import Comparable


class Integer(Comparable):
    @classmethod
    def validate(cls, yaml_node):
        super().validate(yaml_node)
        if (
                not isinstance(yaml_node.value, int) or
                isinstance(yaml_node.value, bool)
        ):
            cls.abort("Expected integer.", yaml_node.loc)
