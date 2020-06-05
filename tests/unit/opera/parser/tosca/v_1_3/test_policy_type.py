from opera.parser.tosca.v_1_3.policy_type import PolicyType


class TestParse:
    def test_full(self, yaml_ast):
        PolicyType.parse(yaml_ast(
            """
            derived_from: policy_type
            description: My desc
            metadata:
              key: value
            version: "1.2"
            properties: {}
            targets: [ node_type, group_type ]
            """
        ))

    def test_minimal(self, yaml_ast):
        PolicyType.parse(yaml_ast(
            """
            derived_from: policy_type
            """
        ))
