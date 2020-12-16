import pathlib
import pytest

from opera.compare.template_comparer import TemplateComparer, TemplateContext
from opera.parser import tosca
from opera.storage import Storage


class TestTemplateCompare:

    def setupdir(self, path, yaml_text):
        pathlib.Path.mkdir(path)
        pathlib.Path.mkdir(path / "files")
        imports = \
            """
            tosca_definitions_version: tosca_simple_yaml_1_3

            capability_types:

                hello_cap:
                    derived_from: tosca.capabilities.Root
                    properties:
                        test1:
                            default: "1"
                            type: string
                        test2:
                            default: "1"
                            type: string
                        test3:
                            default: "1"
                            type: string

            node_types:
                hello_type:
                    derived_from: tosca.nodes.SoftwareComponent
                    properties:
                        time:
                            default: "1"
                            type: string
                        test_map:
                            default:
                            type: map
                    capabilities:
                        test:
                            type: hello_cap
                    interfaces:
                        Standard:
                            inputs:
                                marker:
                                    default: { get_input: marker }
                                    type: string
                                time:
                                    default: { get_property: [SELF, time] }
                                    type: string
                            operations:
                                create: files/create.yaml
                                delete: files/delete.yaml

                hello_type_old:
                    derived_from: hello_type
                    properties:
                        day:
                            default: "1"
                            type: string

                hello_type_new:
                    derived_from: hello_type
                    properties:
                        day:
                            default: "2"
                            type: string
            """
        playbook = \
            """
            ---
            - hosts: all
            gather_facts: false
            tasks:
                - command:
                    cmd: sleep "{{ time }}"
            """
        artefact1 = \
            """
            test: 1
            """
        artefact2 = \
            """
            test: 2
            """

        (path / "types.yaml").write_text(yaml_text(imports))
        (path / "files" / "create.yaml").write_text(yaml_text(playbook))
        (path / "files" / "delete.yaml").write_text(yaml_text(playbook))
        (path / "files" / "file1_1.yaml").write_text(yaml_text(artefact1))
        (path / "files" / "file1_2.yaml").write_text(yaml_text(artefact1))
        (path / "files" / "file2.yaml").write_text(yaml_text(artefact2))



    @pytest.fixture
    def service_template1(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        path = tmp_path / pathlib.Path("t1")
        self.setupdir(path, yaml_text)
        (path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3

            imports:
            - types.yaml

            topology_template:
                inputs:
                    marker:
                        type: string
                        default: default-marker

                node_templates:
                    my-workstation:
                        type: tosca.nodes.Compute
                        attributes:
                            private_address: localhost
                            public_address: localhost

                    hello-1:
                        type: hello_type
                        properties:
                            time: "22"
                        artifacts:
                            def_file:
                                type: tosca.artifacts.File
                                file: files/file1_1.yaml
                        capabilities:
                            test:
                                properties:
                                    test1: "2"
                                    test2: "2"
                        requirements:
                            - host: my-workstation

                    hello-2:
                        type: hello_type_old
                        properties:
                            time: "20"
                        artifacts:
                            def_file:
                                type: tosca.artifacts.File
                                file: files/file1_1.yaml
                        capabilities:
                            test:
                                properties:
                                    test1: "2"
                                    test2: "2"
                        requirements:
                            - host: my-workstation

                    hello-3:
                        type: hello_type
                        properties:
                            time: "3"
                        requirements:
                            - host: my-workstation

                    hello-4:
                        type: hello_type
                        properties:
                            time: "4"
                        requirements:
                            - host: my-workstation

                    hello-6:
                        type: hello_type
                        properties:
                            time: "1"
                        artifacts:
                            def_file:
                                type: tosca.artifacts.File
                                file: files/file2.yaml
                        requirements:
                            - dependency: hello-1
                            - host: my-workstation
            """
        ))
        storage = Storage(path / pathlib.Path(".opera"))
        storage.write("template.yaml", "root_file")
        ast = tosca.load(path, name)
        template = ast.get_template({})
        yield template, path

    @pytest.fixture
    def service_template2(self, tmp_path, yaml_text):
        name = pathlib.PurePath("template.yaml")
        path = tmp_path / pathlib.Path("t2")
        self.setupdir(path, yaml_text)
        (path / name).write_text(yaml_text(
            """
            tosca_definitions_version: tosca_simple_yaml_1_3

            imports:
            - types.yaml

            topology_template:
                inputs:
                    marker:
                        type: string
                        default: default-marker2

                node_templates:
                    my-workstation:
                        type: tosca.nodes.Compute
                        attributes:
                            private_address: localhost
                            public_address: localhost

                    hello-1:
                        type: hello_type
                        properties:
                            time: "20"
                        artifacts:
                            def_file:
                                type: tosca.artifacts.File
                                file: files/file1_2.yaml
                        requirements:
                            - host: my-workstation

                    hello-2:
                        type: hello_type_new
                        properties:
                            time: "20"
                        artifacts:
                            def_file:
                                type: tosca.artifacts.File
                                file: files/file2.yaml
                        capabilities:
                            test:
                                properties:
                                    test1: "3"
                                    test2: "3"
                        requirements:
                            - dependency: hello-1
                            - host: my-workstation

                    hello-3:
                        type: hello_type
                        properties:
                            time: "3"
                        requirements:
                            - host: my-workstation

                    hello-5:
                        type: hello_type
                        properties:
                            time: "1"
                        requirements:
                            - host: my-workstation

                    hello-6:
                        type: hello_type
                        properties:
                            time: "1"
                        artifacts:
                            def_file:
                                type: tosca.artifacts.File
                                file: files/file2.yaml
                        requirements:
                            - dependency: hello-2
                            - host: my-workstation
            """
        ))
        storage = Storage(path / pathlib.Path(".opera"))
        storage.write("template.yaml", "root_file")
        ast = tosca.load(path, name)
        template = ast.get_template({})
        yield template, path

    def test_service_template_comparison(self, service_template1,
                                         service_template2):
        comparer = TemplateComparer()
        context = TemplateContext(service_template1[0],
                                  service_template2[0],
                                  service_template1[1],
                                  service_template2[1])
        equal, diff = comparer.compare_service_template(service_template1[0],
                                                        service_template2[0],
                                                        context)

        assert equal is False

        assert len(diff.changed["nodes"].added) == 1
        assert len(diff.changed["nodes"].deleted) == 1
        assert len(diff.changed["nodes"].changed) == 4

        assert "hello-5" == diff.changed["nodes"].added[0]
        assert "hello-4" == diff.changed["nodes"].deleted[0]

        assert "hello-1" in diff.changed["nodes"].changed
        assert "hello-2" in diff.changed["nodes"].changed
        assert "hello-3" in diff.changed["nodes"].changed
        assert "hello-6" in diff.changed["nodes"].changed

    def test_node_comparison(self, service_template1,
                             service_template2):
        comparer = TemplateComparer()
        node1_1 = service_template1[0].get_node("hello-1")
        node2_1 = service_template2[0].get_node("hello-1")
        context = TemplateContext(node1_1, node2_1,
                                  service_template1[1],
                                  service_template2[1])
        equal, diff = comparer.compare_node(node1_1, node2_1, context)

        assert equal is False

        assert "capabilities" in diff.changed
        assert "interfaces" in diff.changed
        assert "properties" in diff.changed
        assert "requirements" not in diff.changed
        assert "types" not in diff.changed

        node1_2 = service_template1[0].get_node("hello-2")
        node2_2 = service_template2[0].get_node("hello-2")
        context = TemplateContext(node1_2, node2_2,
                                  service_template1[1],
                                  service_template2[1])
        equal, diff = comparer.compare_node(node1_2, node2_2, context)

        assert equal is False

        assert "capabilities" in diff.changed
        assert "interfaces" in diff.changed
        assert "properties" in diff.changed
        assert "requirements" in diff.changed
        assert "types" in diff.changed

    def test_requirement_comparison(self, service_template1,
                                    service_template2):
        comparer = TemplateComparer()
        node1 = service_template1[0].get_node("hello-6")
        node2 = service_template2[0].get_node("hello-6")
        context = TemplateContext(node1, node2,
                                  service_template1[1],
                                  service_template2[1])
        equal, diff = comparer.compare_node(node1, node2, context)

        assert equal is False

        assert "requirements" in diff.changed
        assert "dependency" in diff.changed["requirements"].changed
        assert "target" in diff.changed["requirements"] \
            .changed["dependency"].changed

    def test_interface_comparison(self, service_template1,
                                  service_template2):
        comparer = TemplateComparer()
        node1 = service_template1[0].get_node("hello-1")
        node2 = service_template2[0].get_node("hello-1")
        context = TemplateContext(node1, node2,
                                  service_template1[1],
                                  service_template2[1])
        equal, diff = comparer.compare_node(node1, node2, context)

        assert equal is False

        assert "interfaces" in diff.changed
        assert "create" in diff.changed["interfaces"] \
            .changed["Standard"].changed["operations"].changed
        assert "artifacts" in diff.changed["interfaces"] \
            .changed["Standard"].changed["operations"] \
            .changed["create"].changed
        assert "inputs" in diff.changed["interfaces"] \
            .changed["Standard"].changed["operations"] \
            .changed["create"].changed
