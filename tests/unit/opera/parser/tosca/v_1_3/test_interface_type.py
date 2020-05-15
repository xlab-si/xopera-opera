from opera.parser.tosca.v_1_3.interface_type import InterfaceType


class TestParse:
    def test_full(self, yaml_ast):
        InterfaceType.parse(yaml_ast(
            """
            derived_from: interface_type
            description: My desc
            metadata:
              key: value
            version: "1.2"
            inputs:
              in:
                type: float
            operations: {}
            notifications: {}
            """
        ))

    def test_minimal(self, yaml_ast):
        InterfaceType.parse(yaml_ast(
            """
            derived_from: interface_type
            """
        ))
