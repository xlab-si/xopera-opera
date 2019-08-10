from opera.parser.tosca.v_1_3.interface_definition_for_template import (
    InterfaceDefinitionForTemplate,
)


class TestParse:
    def test_full(self, yaml_ast):
        InterfaceDefinitionForTemplate.parse(yaml_ast(
            """
            inputs:
              in: put
            operations:
              op: artifact
            notifications:
              my_notification:
                description: Notification description
            """
        ))

    def test_minimal(self, yaml_ast):
        InterfaceDefinitionForTemplate.parse(yaml_ast("{}"))
