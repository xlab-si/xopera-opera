from opera.parser.tosca.v_1_3.event_filter_definition import EventFilterDefinition


class TestParse:
    def test_full(self, yaml_ast):
        EventFilterDefinition.parse(yaml_ast(
            """
            node: node_type_name
            requirement: requirement_name
            capability: capability_name
            """
        ))

    def test_minimal(self, yaml_ast):
        EventFilterDefinition.parse(yaml_ast(
            """
            node: node_template_name
            """
        ))
