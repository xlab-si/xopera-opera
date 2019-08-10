from ..string import String


class Status(String):
    VALID_STATES = {"supported", "unsupported", "experimental", "deprecated"}

    @classmethod
    def validate(cls, yaml_node):
        super().validate(yaml_node)
        if yaml_node.value not in cls.VALID_STATES:
            cls.abort(
                "Invalid state: '{}'.".format(yaml_node.value), yaml_node.loc,
            )
