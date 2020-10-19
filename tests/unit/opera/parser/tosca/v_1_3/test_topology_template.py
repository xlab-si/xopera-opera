from opera.parser.tosca.v_1_3.topology_template import TopologyTemplate


class TestParse:
    def test_full(self, yaml_ast):
        TopologyTemplate.parse(yaml_ast(
            """
            description: Topology description
            inputs:
              my_input:
                type: float
                value: 14.3
            node_templates:
              my_node_template:
                type: node.type
            relationship_templates:
              my_rel_template:
                type: rel.type
            groups:
              my_group:
                type: group.type
            policies:
              - my_policy:
                  type: policy.type
            outputs:
              my_output:
                type: string
            """
        ))

    def test_minimal(self, yaml_ast):
        TopologyTemplate.parse(yaml_ast("{}"))
