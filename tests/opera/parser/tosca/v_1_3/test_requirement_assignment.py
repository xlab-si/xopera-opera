import pytest

from opera.error import ParseError
from opera.parser.tosca.v_1_3.requirement_assignment import (
    RequirementAssignment,
)
from opera.parser.yaml.node import Node



class TestNormalize:
    @pytest.mark.parametrize("data", [1, 2.3, True, (), []])
    def test_invalid_data(self, data):
        with pytest.raises(ParseError):
            RequirementAssignment.normalize(Node(data))

    def test_string_normalization(self):
        obj = RequirementAssignment.normalize(Node("string"))

        assert obj.bare == {"node": "string"}

    def test_dict_normalization(self):
        node = Node({})
        obj = RequirementAssignment.normalize(node)

        assert obj == node


class TestParse:
    def test_full(self, yaml_ast):
        RequirementAssignment.parse(yaml_ast(
            """
            capability: my_cap
            node: some_node_template
            relationship: some_relationship_template
            node_filter: {}
            occurrences: [ 2, 3 ]
            """
        ))

    def test_minimal(self, yaml_ast):
        RequirementAssignment.parse(yaml_ast(
            """
            some_node_template
            """
        ))
