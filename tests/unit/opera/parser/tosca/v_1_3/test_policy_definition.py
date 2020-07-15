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
            targets: [node_type_a, node_type_b, node_type_c]
            triggers:
              my_first_trigger:
                event: my_first_trigger
                action:
                  - call_operation: test.interfaces.Test1.test2
              my_second_trigger:
                event: my_second_trigger
                action:
                  - call_operation: test.interfaces.Test2.test1
            """
        ))

    def test_minimal(self, yaml_ast):
        PolicyDefinition.parse(yaml_ast(
            """
            type: policy.type
            """
        ))
