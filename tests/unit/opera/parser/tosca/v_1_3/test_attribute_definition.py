from opera.parser.tosca.v_1_3.attribute_definition import AttributeDefinition


class TestParse:
    def test_full(self, yaml_ast):
        AttributeDefinition.parse(yaml_ast(
            """
            type: my_type
            description: Some desc
            default: 5
            status: deprecated
            key_schema:
              type: integer
            entry_schema:
              type: integer
            """
        ))

    def test_minimal(self, yaml_ast):
        AttributeDefinition.parse(yaml_ast("type: my_type"))
