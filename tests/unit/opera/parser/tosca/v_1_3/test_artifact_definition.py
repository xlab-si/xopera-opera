import pytest

from opera.error import ParseError
from opera.parser.tosca.v_1_3.artifact_definition import ArtifactDefinition
from opera.parser.yaml.node import Node


class TestNormalize:
    @pytest.mark.parametrize("data", [1, 2.3, True, (), []])
    def test_invalid_data(self, data):
        with pytest.raises(ParseError):
            ArtifactDefinition.normalize(Node(data))

    def test_string_normalization(self):
        obj = ArtifactDefinition.normalize(Node("string"))

        assert obj.bare == {
            "type": "tosca.artifacts.File",
            "file": "string",
        }

    def test_dict_normalization(self):
        node = Node({})
        obj = ArtifactDefinition.normalize(node)

        assert obj == node


class TestParse:
    def test_full(self, yaml_ast):
        ArtifactDefinition.parse(yaml_ast(
            """
            description: My arty desc
            type: my.type
            file: some/file
            repository: repo reference
            deploy_path: another/path
            checksum: abcsdfkjrkfsdjdbhf
            checksum_algorithm: SHA256
            properties:
              prop: val
            """
        ))

    def test_minimal(self, yaml_ast):
        ArtifactDefinition.parse(yaml_ast(
            """
            type: my.type
            file: some/file
            """
        ))
