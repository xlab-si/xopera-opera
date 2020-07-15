from opera.parser.tosca.v_1_3.trigger_definition import TriggerDefinition


class TestParse:
    def test_full(self, yaml_ast):
        TriggerDefinition.parse(yaml_ast(
            """
            description: A trigger
            event: trigger
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
                    - my_attribute: [{equal: my_value}]
                    - my_other_attribute: [{equal: my_other_value}]
              period: 60 sec
              evaluations: 2
              method: average
            action:
              - call_operation: test.interfaces.Update.update
              - call_operation: test.interfaces.Upgrade.upgrade
            """
        ))

    def test_minimal(self, yaml_ast):
        TriggerDefinition.parse(yaml_ast(
            """
            event: trigger
            action:
              - call_operation: test.interfaces.Test.test
            """
        ))
