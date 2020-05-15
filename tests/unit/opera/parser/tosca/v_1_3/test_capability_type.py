from opera.parser.tosca.v_1_3.capability_type import CapabilityType


class TestParse:
    def test_full(self, yaml_ast):
        CapabilityType.parse(yaml_ast(
            """
            derived_from: cap_type
            description: My desc
            metadata:
              key: value
            version: "1.2"
            properties:
              prop:
                type: list
            attributes:
              attr:
                type: string
            valid_source_types:
              - my_type
            """
        ))

    def test_minimal(self, yaml_ast):
        CapabilityType.parse(yaml_ast(
            """
            derived_from: cap_type
            """
        ))
