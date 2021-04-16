import pathlib

import pytest

from opera.parser import tosca
from opera.storage import Storage


class TestEvalFunction:
    @pytest.fixture
    def service_template(self, tmp_path, yaml_text):
        name = pathlib.PurePath("service.yaml")
        (tmp_path / name).write_text(yaml_text(
            # language=yaml
            """
            tosca_definitions_version: tosca_simple_yaml_1_3

            node_types:
              eval_test_type:
                derived_from: tosca.nodes.Root
                properties:
                  test_string_input:
                    type: string
                  test_map_input:
                    type: map
                  test_list_input:
                    type: list

            topology_template:
              inputs:
                marker:
                  type: string
              node_templates:
                test_node:
                  type: eval_test_type
                  properties:
                    test_string_input: { get_input: marker }
                    test_map_input:
                      ENV: { get_input: marker }
                      ENV2: test
                      ENV3: { join: [ [ "test", "_", "join" ] ] }
                    test_list_input:
                    - test
                    - { get_input: marker }
                    - { join: [ [ "test", "_", "join" ] ] }
            """
        ))
        storage = Storage(tmp_path / pathlib.Path(".opera"))
        storage.write("service.yaml", "root_file")
        ast = tosca.load(tmp_path, name)
        template = ast.get_template({"marker": "test_input"})
        yield template

    def test_string_eval(self, service_template):
        node = service_template.find_node("test_node")
        string_value = node.get_property(["SELF", "test_string_input"])
        assert isinstance(string_value, str)
        assert string_value == "test_input"

    def test_map_eval(self, service_template):
        node = service_template.find_node("test_node")
        map_value = node.get_property(["SELF", "test_map_input"])
        assert isinstance(map_value, dict)
        assert len(map_value) == 3
        assert map_value["ENV"] == "test_input"
        assert map_value["ENV2"] == "test"
        assert map_value["ENV3"] == "test_join"

    def test_list_eval(self, service_template):
        node = service_template.find_node("test_node")
        list_value = node.get_property(["SELF", "test_list_input"])
        assert isinstance(list_value, list)
        assert len(list_value) == 3
        assert "test_input" in list_value
        assert "test" in list_value
        assert "test_join" in list_value
