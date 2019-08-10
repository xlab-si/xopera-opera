from opera.parser.tosca.v_1_3.node_type import NodeType


class TestParse:
    def test_full(self, yaml_ast):
        NodeType.parse(yaml_ast(
            """
            derived_from: node_type
            description: My desc
            metadata:
              key: value
            version: "1.2"
            attributes: {}
            properties: {}
            requirements:
              - first: requirement_cap_name
              - second:
                  capability: type_name
            interfaces: {}
            artifacts: {}
            """
        ))

    def test_minimal(self, yaml_ast):
        NodeType.parse(yaml_ast(
            """
            derived_from: node_type
            """
        ))
