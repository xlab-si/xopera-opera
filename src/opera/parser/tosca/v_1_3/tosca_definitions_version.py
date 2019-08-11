from ..string import String


class ToscaDefinitionsVersion(String):
    @classmethod
    def validate(cls, yaml_node):
        super().validate(yaml_node)
        if yaml_node.value != "tosca_simple_yaml_1_3":
            cls.abort(
                "Invalid TOSCA version: {}. Expected {}.".format(
                    yaml_node.value, "tosca_simple_yaml_1_3",
                ), yaml_node.loc,
            )

    def eval(self, _reference):
        return self.data
