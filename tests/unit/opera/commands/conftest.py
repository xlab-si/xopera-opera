import shutil
from pathlib import Path, PurePath

import pytest

from opera.storage import Storage


def setupdir(path, yaml_text):
    Path.mkdir(path)
    Path.mkdir(path / "files")
    # language=yaml
    imports = \
        """
        tosca_definitions_version: tosca_simple_yaml_1_3

        node_types:
          hello_node:
            derived_from: tosca.nodes.Root
            properties:
              marker:
                type: string
                default: { get_input: marker }
            interfaces:
              Standard:
                inputs:
                  marker:
                    type: string
                    value: { get_property: [ SELF, marker ] }
                operations:
                  create: files/create.yaml
                  delete: files/delete.yaml
              hello:
                type: hello_interface

        interface_types:
          hello_interface:
            derived_from: tosca.interfaces.Root
            operations:
              hello_operation:
                description: Operation for saying hello
                implementation: files/hello.yaml

        policy_types:
          hello_policy:
            derived_from: tosca.policies.Root
            targets: [ hello_node ]
            triggers:
              hello_trigger:
                description: A trigger for saying hello
                event: hello
                target_filter:
                  node: hello_node
                action:
                  - call_operation:
                      operation: hello.hello_operation
        """
    # language=yaml
    playbook1 = \
        """
        - hosts: all
          gather_facts: false
          tasks:
            - name: Ansible was here
              debug:
                msg: "{{ marker }}"
        """
    # language=yaml
    playbook2 = \
        """
        - hosts: all
          gather_facts: false
          tasks:
            - name: Ansible saying bye bye
              debug:
                msg: "Bye bye!"
        """
    # language=yaml
    playbook3 = \
        """
        - hosts: all
          gather_facts: false
          tasks:
            - name: Say hello
              debug:
                msg: "Hello!"
        """

    (path / "types.yaml").write_text(yaml_text(imports))
    (path / "files" / "create.yaml").write_text(yaml_text(playbook1))
    (path / "files" / "delete.yaml").write_text(yaml_text(playbook2))
    (path / "files" / "hello.yaml").write_text(yaml_text(playbook3))


def prepare_template(path, yaml_text, template):
    name = PurePath("service.yaml")
    (path / name).write_text(yaml_text(template))
    storage = Storage(path / Path(".opera"))
    return template, path, storage


def prepare_csar(path, yaml_text, template):
    # language=yaml
    tosca_meta = \
        """
        TOSCA-Meta-File-Version: 1.1
        CSAR-Version: 1.1
        Created-By: xOpera TOSCA orchestrator
        Entry-Definitions: service.yaml
        """
    Path.mkdir(path / "TOSCA-Metadata")
    (path / "TOSCA-Metadata" / "TOSCA.meta").write_text(yaml_text(tosca_meta))
    name = PurePath("service.yaml")
    (path / name).write_text(yaml_text(template))
    shutil.make_archive(path / "compressed" / "test", "zip", path)
    storage = Storage(path / Path(".opera"))
    return path, storage


@pytest.fixture
def service_template(tmp_path, yaml_text):
    path = tmp_path / Path("t1")
    setupdir(path, yaml_text)
    # language=yaml
    template = \
        """
        tosca_definitions_version: tosca_simple_yaml_1_3

        imports:
          - types.yaml

        topology_template:
          inputs:
            marker:
              type: string
              default: "test-marker"

          node_templates:
            hello:
              type: hello_node

          policies:
            - hello:
                type: hello_policy

          outputs:
            output_marker:
              description: Marker property output
              type: string
              value: { get_property: [ hello, marker ] }
        """
    yield prepare_template(path, yaml_text, template)


@pytest.fixture
def service_template_updated(tmp_path, yaml_text):
    path = tmp_path / Path("t2")
    setupdir(path, yaml_text)
    # language=yaml
    template = \
        """
        tosca_definitions_version: tosca_simple_yaml_1_3

        imports:
          - types.yaml

        topology_template:
          inputs:
            marker:
              type: string
              default: "test-marker"
            another_marker:
              type: string
              default: "test-another-marker"

          node_templates:
            hello:
              type: hello_node

            hello_brother:
              type: hello_node

            hello_sister:
              type: hello_node

          policies:
            - hello:
                type: hello_policy

          outputs:
            output_marker:
              description: Marker property output
              type: string
              value: { get_property: [ hello, marker ] }
        """
    yield prepare_template(path, yaml_text, template)


@pytest.fixture
def csar(tmp_path, yaml_text):
    path = tmp_path / Path("csar")
    setupdir(path, yaml_text)
    # language=yaml
    template = \
        """
        tosca_definitions_version: tosca_simple_yaml_1_3

        imports:
          - types.yaml

        topology_template:
          inputs:
            marker:
              type: string
              default: "test-marker"

          node_templates:
            hello:
              type: hello_node

          policies:
            - hello:
                type: hello_policy

          outputs:
            output_marker:
              description: Marker property output
              type: string
              value: { get_property: [ hello, marker ] }
        """
    yield prepare_csar(path, yaml_text, template)
