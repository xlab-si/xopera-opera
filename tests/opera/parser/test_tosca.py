import pathlib

import pytest

from opera.error import ParseError
from opera.parser import tosca


class TestLoad:
    def test_load_minimal_document(self, tmp_path):
        name = pathlib.PurePath("root.yaml")
        (tmp_path / name).write_text(
            "tosca_definitions_version: tosca_simple_yaml_1_3",
        )

        doc = tosca.load(tmp_path, name)
        assert doc.tosca_definitions_version.data == "tosca_simple_yaml_1_3"

    def test_empty_document_is_invalid(self, tmp_path):
        name = pathlib.PurePath("empty.yaml")
        (tmp_path / name).write_text("{}")
        with pytest.raises(ParseError):
            tosca.load(tmp_path, name)

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
        name = pathlib.PurePath("stdlib.yaml")
        (tmp_path / name).write_text(
            "tosca_definitions_version: tosca_simple_yaml_1_3",
        )

        doc = tosca.load(tmp_path, name)
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
        name = pathlib.PurePath("custom.yaml")
        (tmp_path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            {}:
              my.custom.Type:
                derived_from: {}
            """.format(*typ)
        ))

        doc = tosca.load(tmp_path, name)
        assert doc.dig(typ[0], "my.custom.Type") is not None

    def test_loads_template_part(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        (tmp_path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            topology_template:
              node_templates:
                my_node:
                  type: tosca.nodes.SoftwareComponent
            """
        ))

        doc = tosca.load(tmp_path, name)
        assert doc.topology_template.node_templates["my_node"] is not None

    def test_load_from_csar_subfolder(self, tmp_path, yaml_text):
        name = pathlib.PurePath("sub/folder/file.yaml")
        (tmp_path / name).parent.mkdir(parents=True)
        (tmp_path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            imports:
              - imp.yaml
            """
        ))
        (tmp_path / "sub/folder/imp.yaml").write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            data_types:
              my_type:
                derived_from: tosca.datatypes.xml
            """
        ))

        doc = tosca.load(tmp_path, name)
        assert doc.data_types["my_type"]
