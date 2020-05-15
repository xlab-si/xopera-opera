from opera.parser.tosca.v_1_3.relationship_type import RelationshipType


class TestParse:
    def test_full(self, yaml_ast):
        RelationshipType.parse(yaml_ast(
            """
            derived_from: relationship_type
            description: My desc
            metadata:
              key: value
            version: "1.2"
            properties: {}
            attributes: {}
            interfaces: {}
            valid_target_types: [ a, b, c ]
            """
        ))

    def test_minimal(self, yaml_ast):
        RelationshipType.parse(yaml_ast(
            """
            derived_from: relationship_type
            """
        ))
