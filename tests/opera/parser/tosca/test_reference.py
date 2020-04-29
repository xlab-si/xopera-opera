import pytest

from opera.error import ParseError
from opera.parser.tosca.reference import (
    DataTypeReference, DataTypeReferenceWrapper, Reference, ReferenceWrapper,
)
from opera.parser.tosca.type import Type
from opera.parser.tosca.v_1_3.service_template import ServiceTemplate
from opera.parser.yaml.node import Node


class TestReferenceWrapperResolveReference:
    def test_valid_type_reference(self, yaml_ast, tmp_path):
        service = ServiceTemplate.parse(yaml_ast(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            node_types:
              my.Type:
                derived_from: tosca.nodes.Root
            """
        ), tmp_path, tmp_path, set())[0]
        ref = ReferenceWrapper("my.Type", None)
        ref.section_path = ("node_types",)

        assert service.node_types["my.Type"] == ref.resolve_reference(service)

    def test_valid_template_reference(self, yaml_ast, tmp_path):
        service = ServiceTemplate.parse(yaml_ast(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            topology_template:
              node_templates:
                my_node:
                  type: tosca.nodes.Root
            """
        ), tmp_path, tmp_path, set())[0]
        ref = ReferenceWrapper("my_node", None)
        ref.section_path = ("topology_template", "node_templates")

        target = service.topology_template.node_templates["my_node"]
        assert target == ref.resolve_reference(service)

    def test_invalid_reference(self, yaml_ast, tmp_path):
        service = ServiceTemplate.parse(yaml_ast(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            node_types:
              my.Type:
                derived_from: tosca.nodes.Root
            """
        ), tmp_path, tmp_path, set())[0]
        ref = ReferenceWrapper("INVALID", None)
        ref.section_path = ("node_types",)

        with pytest.raises(ParseError):
            ref.resolve_reference(service)


class TestDataTypeReferenceWrapperResolveReference:
    @pytest.mark.parametrize("typ", [
        "string", "integer", "float", "boolean", "null",
        "timestamp", "version", "range", "list", "map", "scalar-unit.size",
        "scalar-unit.time", "scalar-unit.frequency", "scalar-unit.bitrate",
    ])
    def test_valid_internal_data_type_reference(self, typ):
        ref = DataTypeReferenceWrapper(typ, None)
        ref.section_path = ("data_types",)

        result = ref.resolve_reference(None)

        assert isinstance(result, Type)
        assert typ == result.data

    def test_valid_user_data_type_reference(self, yaml_ast, tmp_path):
        service = ServiceTemplate.parse(yaml_ast(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            data_types:
              my.Type:
                derived_from: float
            """
        ), tmp_path, tmp_path, set())[0]
        ref = DataTypeReferenceWrapper("my.Type", None)
        ref.section_path = ("data_types",)

        assert service.data_types["my.Type"] == ref.resolve_reference(service)


class TestReferenceInit:
    @pytest.mark.parametrize("path", [
        ("single",), ("multi", "path"), ("a", "b", "c", "d"),
    ])
    def test_valid_init(self, path):
        assert Reference(*path).section_path == path

    def test_empty_path(self):
        with pytest.raises(AssertionError):
            Reference()

    @pytest.mark.parametrize("path", [
        (1,), (2.3,), (False,), ((),), ([],), ({},), ("a", 1),
    ])
    def test_invalid_path_components(self, path):
        with pytest.raises(AssertionError):
            Reference(*path)


class TestReferenceParse:
    @pytest.mark.parametrize("path", [
        ("single",), ("multi", "path"), ("a", "b", "c", "d"),
    ])
    def test_parse(self, path):
        assert Reference(*path).parse(Node("name")).section_path == path
