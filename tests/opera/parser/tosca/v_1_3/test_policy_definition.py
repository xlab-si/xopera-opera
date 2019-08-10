from opera.parser.tosca.v_1_3.policy_definition import PolicyDefinition


class TestParse:
    def test_full(self, yaml_ast):
        PolicyDefinition.parse(yaml_ast(
            """
            type: policy.type
            description: Some muttering
            metadata: {}
            properties:
              prop: 6.7
            """
        ))

    def test_minimal(self, yaml_ast):
        PolicyDefinition.parse(yaml_ast(
            """
            type: policy.type
            """
        ))
