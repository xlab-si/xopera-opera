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
            triggers:
              my_trigger:
                description: A trigger
                event: my_trigger
                schedule:
                  start_time: 2020-04-08T21:59:43.10-06:00
                  end_time: 2022-04-08T21:59:43.10-06:00
                target_filter:
                  node: node
                  requirement: my_requirement
                  capability: my_capability
                condition:
                  constraint:
                    - not:
                      - and:
                        - my_attribute: [ in_range: [1, 50] ]
                        - my_other_attribute: [ equal: my_other_value ]
                  period: 60 sec
                  evaluations: 2
                  method: average
                action:
                  - call_operation:
                      operation: test.interfaces.test.Test.test
                      inputs:
                        test_input: { get_property: [ SELF, test_property ] }
                  - delegate:
                      workflow: delegate_workflow_name
                      inputs:
                        test_input: { get_input: [ SELF, test_input ] }
            """
        ))

    def test_minimal(self, yaml_ast):
        PolicyType.parse(yaml_ast(
            """
            derived_from: policy_type
            """
        ))
