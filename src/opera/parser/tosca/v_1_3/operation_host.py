from opera.constants import OperationHost as OperationHostConstant
from ..string import String


class OperationHost(String):
    VALID_HOSTS = [h.value for h in OperationHostConstant]

    @classmethod
    def validate(cls, yaml_node):
        super().validate(yaml_node)
        if yaml_node.value not in cls.VALID_HOSTS:
            cls.abort(
                f"Invalid operation host: {yaml_node.value}. Use any from: {', '.join(cls.VALID_HOSTS)}", yaml_node.loc
            )
