import pytest
import pathlib

from opera.parser import tosca
from opera.storage import Storage


def setupdir(path, yaml_text):
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


def prepare_template(path, yaml_text, template):
    name = pathlib.PurePath("template.yaml")
    (path / name).write_text(yaml_text(template))
    storage = Storage(path / pathlib.Path(".opera"))
    storage.write("template.yaml", "root_file")
    ast = tosca.load(path, name)
    template = ast.get_template({})
    topology = template.instantiate(storage)
    return template, topology, path

@pytest.fixture
def service_template1(tmp_path, yaml_text):
    path = tmp_path / pathlib.Path("t1")
    setupdir(path, yaml_text)
    template = \
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
    yield prepare_template(path, yaml_text, template)


@pytest.fixture
def service_template2(tmp_path, yaml_text):
    path = tmp_path / pathlib.Path("t2")
    setupdir(path, yaml_text)
    template = \
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
    yield prepare_template(path, yaml_text, template)
