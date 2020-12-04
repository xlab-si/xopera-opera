import pathlib

import pytest

from opera.error import ParseError
from opera.parser import tosca
from opera.storage import Storage


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

    def test_duplicate_import(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        (tmp_path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            imports: [ template.yaml ]
            """
        ))
        tosca.load(tmp_path, name)

    def test_imports_from_multiple_levels(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        (tmp_path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            imports:
              - subfolder/a.yaml
              - subfolder/b.yaml
            """
        ))
        (tmp_path / "subfolder").mkdir()
        (tmp_path / "subfolder/a.yaml").write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            imports:
              - b.yaml
            """
        ))
        (tmp_path / "subfolder/b.yaml").write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            data_types:
              my_type:
                derived_from: tosca.datatypes.xml
            """
        ))

        tosca.load(tmp_path, name)

    def test_merge_topology_template(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        (tmp_path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            imports:
              - merge.yaml
            topology_template:
              inputs:
                some-input:
                  type: string
              node_templates:
                my_node:
                  type: tosca.nodes.SoftwareComponent              
            """
        ))
        (tmp_path / "merge.yaml").write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            topology_template:
              inputs:
                other-input:
                  type: string
              node_templates:
                other_node:
                  type: tosca.nodes.SoftwareComponent 
            """
        ))
        tosca.load(tmp_path, name)

    def test_merge_duplicate_node_templates_invalid(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        (tmp_path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            imports:
              - merge1.yaml
              - merge2.yaml
            topology_template:
              node_templates:
                my_node:
                  type: tosca.nodes.SoftwareComponent              
            """
        ))
        (tmp_path / "merge1.yaml").write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            topology_template:
              node_templates:
                other_node:
                  type: tosca.nodes.SoftwareComponent 
            """
        ))
        (tmp_path / "merge2.yaml").write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            topology_template:
              node_templates:
                other_node:
                  type: tosca.nodes.SoftwareComponent 
            """
        ))
        with pytest.raises(ParseError):        
            tosca.load(tmp_path, name)


class TestExecute:
    def test_undefined_required_properties1(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        (tmp_path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            node_types:
              my_node_type:
                derived_from: tosca.nodes.Root
                attributes:
                  test_attribute:
                    type: boolean
                properties:
                  test_property1:
                    type: integer
                    default: 42
                    required: false
                  test_property2:
                    type: float
                    default: 42.0
                    required: true
                  test_property3:
                    type: string
                    required: true
            topology_template:
              node_templates:
                my_node_template:
                  type: my_node_type             
            """
        ))
        storage = Storage(tmp_path / pathlib.Path(".opera"))
        storage.write("template.yaml", "root_file")
        ast = tosca.load(tmp_path, name)
        with pytest.raises(ParseError, match="Missing a required property: "
                                             "test_property3"):
            ast.get_template({})

    def test_undefined_required_properties2(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        (tmp_path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            node_types:
              my_node_type:
                derived_from: tosca.nodes.Root
                properties:
                  test_prop1:
                    type: integer
                    required: false
                  test_prop2:
                    type: float
                    default: 42.0
                  test_prop3:
                    type: string
            topology_template:
              node_templates:
                my_node_template:
                  type: my_node_type             
            """
        ))
        storage = Storage(tmp_path / pathlib.Path(".opera"))
        storage.write("template.yaml", "root_file")
        ast = tosca.load(tmp_path, name)
        with pytest.raises(ParseError, match="Missing a required property: "
                                             "test_prop3"):
            ast.get_template({})

    def test_undefined_required_properties3(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        (tmp_path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            node_types:
              my_node_type:
                derived_from: tosca.nodes.Root
                properties:
                  property1:
                    type: integer
                  property2:
                    type: float
                  property3:
                    type: string
            topology_template:
              node_templates:
                my_node_template:
                  type: my_node_type  
                  properties:
                    property1: 42
                    property2: 42.0        
            """
        ))
        storage = Storage(tmp_path / pathlib.Path(".opera"))
        storage.write("template.yaml", "root_file")
        ast = tosca.load(tmp_path, name)
        with pytest.raises(ParseError, match="Missing a required property: "
                                             "property3"):
            ast.get_template({})
