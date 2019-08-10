import pytest

from opera.error import ParseError
from opera.parser.tosca.v_1_3.requirement_definition import (
    RequirementDefinition,
)
from opera.parser.yaml.node import Node


class TestNormalize:
    @pytest.mark.parametrize("data", [1, 2.3, True, (), []])
    def test_invalid_data(self, data):
        with pytest.raises(ParseError):
            RequirementDefinition.normalize(Node(data))

    def test_string_normalization(self):
        obj = RequirementDefinition.normalize(Node("string"))

        assert obj.bare == {"capability": "string"}

    def test_dict_normalization(self):
        node = Node({})
        obj = RequirementDefinition.normalize(node)

        assert obj == node


class TestParse:
    def test_full(self, yaml_ast):
        RequirementDefinition.parse(yaml_ast(
            """
            capability: my_cap_type
            node: my_node_type
            relationship: my_rel_type
            occurrences: [ 2, 5 ]
            """
        ))

    def test_minimal(self, yaml_ast):
        RequirementDefinition.parse(yaml_ast(
            """
            capability: my_cap_type
            """
        ))
