import pathlib

import pytest

from opera.error import DataError
from opera.parser import tosca
from opera.storage import Storage


class TestAttributeMapping:
    @pytest.fixture
    def service_template(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        (tmp_path / name).write_text(yaml_text(
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
        ast = tosca.load(tmp_path, name)
        template = ast.get_template({})
        topology = template.instantiate(storage)
        yield template

    def test_map_attribute_node(self, service_template):
        node = service_template.find_node("my_node")
        node.map_attribute(["SELF", "colour"], "green")
        assert "green" == node.get_attribute(["SELF", "colour"])

    @pytest.mark.parametrize("host",
                             ["SOURCE", "TARGET", "HOST" "my_collector",
                              "other"])
    def test_map_attribute_node_bad_host(self, service_template, host):
        node = service_template.find_node("my_node")
        with pytest.raises(DataError, match="Accessing non-local stuff"):
          node.map_attribute([host, "colour"], "black")

    def test_map_attribute_node_bad_attribute(self, service_template):
        node = service_template.find_node("my_node")
        with pytest.raises(DataError, match="Cannot find attribute"):
          node.map_attribute(["SELF", "volume"], "loud")

    def test_map_attribute_relationship_source(self, service_template):
      node_source = service_template.find_node("my_collector")
      node_source_instance = next(iter(node_source.instances.values()))
      relationship_instance = next(
        iter(node_source_instance.out_edges["my_target"].values()))

      relationship_instance.map_attribute(["SOURCE", "colour"], "ochre")

      assert "ochre" == node_source.get_attribute(["SELF", "colour"])

    def test_map_attribute_relationship_target(self, service_template):
      node_target = service_template.find_node("my_node")
      node_source = service_template.find_node("my_collector")
      node_source_instance = next(iter(node_source.instances.values()))
      relationship_instance = next(
        iter(node_source_instance.out_edges["my_target"].values()))

      relationship_instance.map_attribute(["TARGET", "colour"], "magenta")

      assert "magenta" == node_target.get_attribute(["SELF", "colour"])

    def test_map_attribute_relationship_self(self, service_template):
      node_source = service_template.find_node("my_collector")
      node_source_instance = next(iter(node_source.instances.values()))
      relationship_instance = next(
        iter(node_source_instance.out_edges["my_target"].values()))

      relationship_instance.map_attribute(["SELF", "colour"], "steampunk")

      assert "steampunk" == relationship_instance.get_attribute(
          ["SELF", "colour"])

    @pytest.mark.parametrize("host",
                             ["HOST", "my_node", "my_collector", "other"])
    def test_map_attribute_relationship_bad_host(self, service_template, host):
      node_source = service_template.find_node("my_collector")
      node_source_instance = next(iter(node_source.instances.values()))
      relationship_instance = next(
        iter(node_source_instance.out_edges["my_target"].values()))

      with pytest.raises(DataError, match="Accessing non-local stuff"):
        relationship_instance.map_attribute([host, "colour"], "ochre")

    @pytest.mark.parametrize("host, pattern", [
                                ("SELF", "Instance has no 'volume' attribute"),
                                ("SOURCE", "Cannot find attribute 'volume'."),
                                ("TARGET", "Cannot find attribute 'volume'.")
                            ])
    def test_map_attr_rel_bad_attr(self, service_template, host, pattern):
      node_source = service_template.find_node("my_collector")
      node_source_instance = next(iter(node_source.instances.values()))
      relationship_instance = next(
        iter(node_source_instance.out_edges["my_target"].values()))

      with pytest.raises(DataError, match=pattern):
        relationship_instance.map_attribute([host, "volume"], "quiet")
