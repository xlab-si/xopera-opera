import pytest

from opera.parser.tosca.v_1_3.property_definition import PropertyDefinition


class TestParse:
    def test_full(self, yaml_ast):
        PropertyDefinition.parse(yaml_ast(
            """
            type: map
            description: My description
            required: false
            default: { a: 3 }
            status: supported
            constraints: []
            key_schema:
              type: string
            entry_schema:
              type: integer
            external_schema: some schema
            metadata: {}
            """
        ))

    def test_minimal(self, yaml_ast):
        PropertyDefinition.parse(yaml_ast(
            """
            type: map
            """
        ))
