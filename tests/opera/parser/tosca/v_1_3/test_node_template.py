from opera.parser.tosca.v_1_3.node_template import NodeTemplate


class TestParse:
    def test_full(self, yaml_ast):
        NodeTemplate.parse(yaml_ast(
            """
            type: node.type
            description: Text
            metadata: {}
            directives: []
            properties: {}
            attributes: {}
            requirements: []
            capabilities: {}
            interfaces: {}
            artifacts: {}
            node_filter: {}
            copy: template_name
            """
        ))

    def test_minimal(self, yaml_ast):
        NodeTemplate.parse(yaml_ast(
            """
            type: node.type
            """
        ))
