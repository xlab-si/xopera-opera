from opera.parser.tosca.v_1_3.notification_definition import (
    NotificationDefinition,
)


class TestParse:
    def test_full(self, yaml_ast):
        NotificationDefinition.parse(yaml_ast(
            """
            description: Bla bla bla
            implementation: path/to/artifact
            outputs:
              data: [ SELF, attribute ]
            """
        ))

    def test_minimal(self, yaml_ast):
        NotificationDefinition.parse(yaml_ast("{}"))
