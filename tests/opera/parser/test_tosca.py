import pytest

from opera.error import ParseError
from opera.parser import tosca


class TestLoad:
    def test_load_minimal_document(self, tmp_path):
        root = tmp_path / "root.yaml"
        root.write_text("tosca_definitions_version: tosca_simple_yaml_1_3")

        doc = tosca.load(root.parent, root.name)
        assert doc.tosca_definitions_version.data == "tosca_simple_yaml_1_3"

    def test_empty_document_is_invalid(self, tmp_path):
        root = tmp_path / "root.yaml"
        root.write_text("{}")
        with pytest.raises(ParseError):
            tosca.load(root.parent, root.name)

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

        doc = tosca.load(root.parent, root.name)
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

        doc = tosca.load(root.parent, root.name)
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

        doc = tosca.load(root.parent, root.name)
        assert doc.topology_template.node_templates["my_node"] is not None
