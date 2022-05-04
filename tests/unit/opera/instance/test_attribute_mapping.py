import pathlib

import pytest
from opera_tosca_parser.commands.parse import parse_service_template

from opera.error import DataError
from opera.storage import Storage
from opera.instance.topology import Topology


class TestAttributeMapping:
    @pytest.fixture
    def service_template(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        (tmp_path / name).write_text(yaml_text(
            # language=yaml
            """
            tosca_definitions_version: tosca_simple_yaml_1_3
            node_types:
              my_base_type:
                derived_from: tosca.nodes.Root
                attributes:
                  colour:
                    type: string
              my_node_type:
                derived_from: my_base_type
              my_collector_node_type:
                derived_from: my_base_type
                requirements:
                  - my_target:
                      capability: tosca.capabilities.Root
                      relationship: my_relationship_type
            relationship_types:
              my_relationship_type:
                derived_from: tosca.relationships.Root
                attributes:
                  colour:
                    type: string

            topology_template:
              node_templates:
                my_node:
                  type: my_node_type
                my_collector:
                  type: my_collector_node_type
                  requirements:
                    - my_target: my_node
            """
        ))
        storage = Storage(tmp_path / pathlib.Path(".opera"))
        storage.write("template.yaml", "root_file")
        template, _ = parse_service_template((tmp_path / name), {})
        topology_template = Topology.instantiate(template, storage)
        yield topology_template

    def test_map_attribute_node(self, service_template):
        node = service_template.find_node("my_node")
        node.map_attribute(["SELF", "colour"], "green")
        assert node.get_attribute(["SELF", "colour"]) == "green"

    @pytest.mark.parametrize("host", [
        ("SOURCE", "HOST as the attribute's 'host' is not yet supported"),
        ("TARGET", "HOST as the attribute's 'host' is not yet supported"),
        ("HOST", "HOST as the attribute's 'host' is not yet supported"),
        ("my_collector", "The attribute's 'host' should be set to one of"),
        ("other", "The attribute's 'host' should be set to one of")
    ])
    def test_map_attribute_node_bad_host(self, service_template, host):
        node = service_template.find_node("my_node")
        with pytest.raises(DataError, match="Invalid attribute host for attribute mapping"):
            node.map_attribute([host, "colour"], "black")

    def test_map_attribute_node_bad_attribute(self, service_template):
        node = service_template.find_node("my_node")
        with pytest.raises(DataError, match="Cannot find attribute"):
            node.map_attribute(["SELF", "volume"], "loud")

    def test_map_attribute_relationship_source(self, service_template):
        node_source_instance = service_template.find_node("my_collector")
        relationship_instance = next(iter(node_source_instance.out_edges["my_target"].values()))

        relationship_instance.map_attribute(["SOURCE", "colour"], "ochre")

        assert node_source_instance.get_attribute(["SELF", "colour"]) == "ochre"

    def test_map_attribute_relationship_target(self, service_template):
        node_target = service_template.find_node("my_node")
        node_source_instance = service_template.find_node("my_collector")
        relationship_instance = next(iter(node_source_instance.out_edges["my_target"].values()))

        relationship_instance.map_attribute(["TARGET", "colour"], "magenta")

        assert node_target.get_attribute(["SELF", "colour"]) == "magenta"

    def test_map_attribute_relationship_self(self, service_template):
        node_source_instance = service_template.find_node("my_collector")
        relationship_instance = next(iter(node_source_instance.out_edges["my_target"].values()))

        relationship_instance.map_attribute(["SELF", "colour"], "steampunk")

        assert relationship_instance.get_attribute(["SELF", "colour"]) == "steampunk"

    @pytest.mark.parametrize("host", [
        ("HOST", "HOST as the attribute's 'host' is not yet supported"),
        ("my_node", "The attribute's 'host' should be set to one of"),
        ("my_collector", "The attribute's 'host' should be set to one of"),
        ("other", "The attribute's 'host' should be set to one of")
    ])
    def test_map_attribute_relationship_bad_host(self, service_template, host):
        node_source_instance = service_template.find_node("my_collector")
        relationship_instance = next(iter(node_source_instance.out_edges["my_target"].values()))

        with pytest.raises(DataError, match="Invalid attribute host for attribute mapping"):
            relationship_instance.map_attribute([host, "colour"], "ochre")

    @pytest.mark.parametrize("host", ["SELF", "SOURCE", "TARGET"])
    def test_map_attr_rel_bad_attr(self, service_template, host):
        node_source_instance = service_template.find_node("my_collector")
        relationship_instance = next(iter(node_source_instance.out_edges["my_target"].values()))

        with pytest.raises(DataError, match="Cannot find attribute 'volume' among"):
            print(relationship_instance.map_attribute([host, "volume"], "quiet"))
            relationship_instance.map_attribute([host, "volume"], "quiet")
