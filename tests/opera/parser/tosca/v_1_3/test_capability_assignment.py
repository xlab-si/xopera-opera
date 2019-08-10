from opera.parser.tosca.v_1_3.capability_assignment import CapabilityAssignment


class TestParse:
    def test_full(self, yaml_ast):
        CapabilityAssignment.parse(yaml_ast(
            """
            properties:
              prop: value
            attributes:
              attr: value
            occurrences: [ 0, UNBOUNDED ]
            """
        ))

    def test_minimal(self, yaml_ast):
        CapabilityAssignment.parse(yaml_ast("{}"))
