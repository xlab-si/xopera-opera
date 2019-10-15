import pathlib

import pytest

from opera.csar import ToscaCsar
from opera.error import ParseError
from opera.parser.parser import ToscaParser

_RESOURCE_DIRECTORY = pathlib.Path(__file__).parent.parent.parent.absolute() / "resources/"


class TestMinimal:
    def test_minimal_document(self, tmp_path):
        root = tmp_path / "root.yaml"
        root.write_text("tosca_definitions_version: tosca_simple_yaml_1_3")

        csar = ToscaCsar.load(root, strict=True)
        doc = ToscaParser.parse(csar)
        assert doc.tosca_definitions_version.data == "tosca_simple_yaml_1_3"

    def test_empty_document_is_invalid(self, tmp_path):
        root = tmp_path / "root.yaml"
        root.write_text("{}")
        csar = ToscaCsar.load(root, strict=True)
        with pytest.raises(ParseError):
            ToscaParser.parse(csar)

    @pytest.mark.parametrize("typ", [
        ("data_types", "tosca.datatypes.xml"),
        ("artifact_types", "tosca.artifacts.Implementation.Bash"),
        ("capability_types", "tosca.capabilities.Node"),
        ("relationship_types", "tosca.relationships.HostedOn"),
        ("interface_types", "tosca.interfaces.Root"),
        ("node_types", "tosca.nodes.Root"),
        ("group_types", "tosca.groups.Root"),
        ("policy_types", "tosca.policies.Root"),
    ])
    def test_stdlib_is_present(self, tmp_path, typ):
        root = tmp_path / "root.yaml"
        root.write_text("tosca_definitions_version: tosca_simple_yaml_1_3")

        csar = ToscaCsar.load(root, strict=True)
        doc = ToscaParser.parse(csar)
        assert doc.dig(*typ) is not None

    @pytest.mark.parametrize("typ", [
        ("data_types", "tosca.datatypes.xml"),
        ("artifact_types", "tosca.artifacts.Implementation.Bash"),
        ("capability_types", "tosca.capabilities.Node"),
        ("relationship_types", "tosca.relationships.HostedOn"),
        ("interface_types", "tosca.interfaces.Root"),
        ("node_types", "tosca.nodes.Root"),
        ("group_types", "tosca.groups.Root"),
        ("policy_types", "tosca.policies.Root"),
    ])
    def test_custom_type_is_present(self, tmp_path, yaml_text, typ):
        root = tmp_path / "root.yaml"
        root.write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            {}:
              my.custom.Type:
                derived_from: {}
            """.format(*typ)
        ))

        csar = ToscaCsar.load(root, strict=True)
        doc = ToscaParser.parse(csar)
        assert doc.dig(typ[0], "my.custom.Type") is not None

    def test_loads_template_part(self, tmp_path, yaml_text):
        root = tmp_path / "root.yaml"
        root.write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            topology_template:
              node_templates:
                my_node:
                  type: tosca.nodes.SoftwareComponent
            """
        ))

        csar = ToscaCsar.load(root, strict=True)
        doc = ToscaParser.parse(csar)
        assert doc.topology_template.node_templates["my_node"] is not None


class TestComplex:
    @pytest.mark.parametrize("csar_dir", ["mini"])
    def test_parse_success(self, csar_dir):
        root = _RESOURCE_DIRECTORY / "csar" / csar_dir
        csar = ToscaCsar.load(root, strict=True)
        ToscaParser.parse(csar)

    @pytest.mark.parametrize("csar_dir", ["invalidkey", "absolutepath"])
    def test_parse_failure(self, csar_dir):
        root = _RESOURCE_DIRECTORY / "csar" / csar_dir
        csar = ToscaCsar.load(root, strict=True)
        with pytest.raises(ParseError):
            ToscaParser.parse(csar)
