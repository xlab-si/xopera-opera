from .comparable import Comparable


class String(Comparable):
    @classmethod
    def validate(cls, yaml_node):
        super().validate(yaml_node)
        if not isinstance(yaml_node.value, str):
            cls.abort("Expected string input", yaml_node.loc)
