from opera.parser.tosca.v_1_3.group_type import GroupType


class TestParse:
    def test_full(self, yaml_ast):
        GroupType.parse(yaml_ast(
            """
            derived_from: group_type
            description: My desc
            metadata:
              key: value
            version: "1.2"
            attributes: {}
            properties: {}
            members: [node_type_a, node_type_b, node_type_c]
            """
        ))

    def test_minimal(self, yaml_ast):
        GroupType.parse(yaml_ast(
            """
            derived_from: group_type
            """
        ))
