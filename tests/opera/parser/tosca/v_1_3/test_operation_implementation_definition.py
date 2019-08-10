import pytest

from opera.error import ParseError
from opera.parser.tosca.v_1_3.operation_implementation_definition import (
    OperationImplementationDefinition,
)
from opera.parser.yaml.node import Node


class TestNormalize:
    @pytest.mark.parametrize("data", [1, 2.3, True, (), []])
    def test_invalid_data(self, data):
        with pytest.raises(ParseError):
            OperationImplementationDefinition.normalize(Node(data))

    def test_string_normalization(self):
        obj = OperationImplementationDefinition.normalize(Node("string"))

        assert obj.bare == {"primary": "string"}

    def test_dict_normalization(self):
        node = Node({})
        obj = OperationImplementationDefinition.normalize(node)

        assert obj == node


class TestParse:
    def test_full(self, yaml_ast):
        OperationImplementationDefinition.parse(yaml_ast(
            """
            primary: artifact
            dependencies:
              - first
              - second
            timeout: 4
            operation_host: ORCHESTRATOR
            """
        ))

    def test_minimal(self, yaml_ast):
        OperationImplementationDefinition.parse(yaml_ast("{}"))
