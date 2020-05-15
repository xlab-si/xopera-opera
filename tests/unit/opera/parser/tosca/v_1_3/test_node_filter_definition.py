from opera.parser.tosca.v_1_3.node_filter_definition import (
    NodeFilterDefinition,
)


class TestParse:
    def test_full(self, yaml_ast):
        NodeFilterDefinition.parse(yaml_ast(
            """
            properties:
              - num_cpus: { in_range: [ 3, 6 ] }
            capabilities: []
            """
        ))

    def test_minimal(self, yaml_ast):
        NodeFilterDefinition.parse(yaml_ast("{}"))
