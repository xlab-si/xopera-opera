import pytest

from opera.error import ParseError
from opera.parser.tosca.v_1_3.service_template import ServiceTemplate
from opera.parser.yaml.node import Node


class TestNormalizeDefinition:
    def test_noop_for_dicts_with_no_dsl_definitions(self):
        assert ServiceTemplate.normalize(Node({})).bare == {}

    def test_dsl_definitions_removal(self):
        assert ServiceTemplate.normalize(Node({
            Node("dsl_definitions"): "data",
        })).bare == {}

    @pytest.mark.parametrize("data", [123, 1.4, []])
    def test_failure_with_non_dict_data(self, data):
        with pytest.raises(ParseError):
            ServiceTemplate.normalize(Node(data))


class TestParse:
    def test_full(self, yaml_ast):
        ServiceTemplate.parse(yaml_ast(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            namespace: some.namespace
            metadata: {}
            description: Text here
            dsl_definitions:
              arbitrary_data: can
              be: here
              since:
                - it
                - is
                - stripped: from
                  the: doc
            repositories: {}
            imports: []
            artifact_types: {}
            data_types: {}
            capability_types: {}
            interface_types: {}
            relationship_types: {}
            node_types: {}
            group_types: {}
            policy_types: {}
            topology_template: {}
            """
        ), None, None)

    def test_minimal(self, yaml_ast):
        ServiceTemplate.parse(yaml_ast(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            """
        ), None, None)


class TestMerge:
    def test_valid_section_merge(self, yaml_ast):
        template = ServiceTemplate.parse(yaml_ast(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            node_types:
              type_a:
                derived_from: a
            """
        ), None, None)
        template.merge(ServiceTemplate.parse(yaml_ast(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            node_types:
              type_b:
                derived_from: b
            """
        ), None, None))

        assert template.node_types.bare == {
            "type_a": {"derived_from": "a"},
            "type_b": {"derived_from": "b"},
        }

    def test_valid_merge(self, yaml_ast):
        template = ServiceTemplate.parse(yaml_ast(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            data_types:
              type_a:
                derived_from: a
            """
        ), None, None)
        template.merge(ServiceTemplate.parse(yaml_ast(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            node_types:
              type_a:
                derived_from: a
            """
        ), None, None))

        assert template.node_types.bare == {"type_a": {"derived_from": "a"}}
        assert template.data_types.bare == {"type_a": {"derived_from": "a"}}

    def test_duplicates(self, yaml_ast):
        with pytest.raises(ParseError, match="type_a"):
            ServiceTemplate.parse(yaml_ast(
                """
                tosca_definitions_version: tosca_simple_yaml_1_3
                node_types:
                  type_a:
                    derived_from: a
                """
            ), None, None).merge(ServiceTemplate.parse(yaml_ast(
                """
                tosca_definitions_version: tosca_simple_yaml_1_3
                node_types:
                  type_a:
                    derived_from: b
                """
            ), None, None))
