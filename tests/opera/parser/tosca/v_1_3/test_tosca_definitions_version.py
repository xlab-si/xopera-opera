import pytest

from opera.error import ParseError
from opera.parser.tosca.v_1_3.tosca_definitions_version import (
    ToscaDefinitionsVersion,
)
from opera.parser.yaml.node import Node


class TestValidate:
    def test_valid_tosca_versions(self):
        ToscaDefinitionsVersion.validate(Node("tosca_simple_yaml_1_3"))

    @pytest.mark.parametrize(
        "version", [
            "", "  ", "a", "tosca_simple_yaml_1_4", 123, "abc", {}, [],
            "tosca_simple_yaml_1_4", "tosca_simple_yaml_2", "tosca_yaml_1_2",
            "tosca_simple_yaml_1_0", "tosca_simple_yaml_1_1",
            "tosca_simple_yaml_1_2",
        ],
    )
    def test_invalid_tosca_versions(self, version):
        with pytest.raises(ParseError):
            ToscaDefinitionsVersion.validate(Node(version))
