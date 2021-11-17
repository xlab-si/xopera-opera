import pathlib

import pytest

from opera.parser import tosca
from opera.storage import Storage


class TestNodePolicies:
    @pytest.fixture
    def service_template(self, tmp_path, yaml_text):
        name = pathlib.PurePath("service.yaml")
        (tmp_path / name).write_text(yaml_text(
            # language=yaml
            """
            tosca_definitions_version: tosca_simple_yaml_1_3

            node_types:
              steampunk.nodes.VM:
                derived_from: tosca.nodes.Compute
                interfaces:
                  Standard:
                    type: tosca.interfaces.node.lifecycle.Standard
                    operations:
                      create: playbooks/create.yaml
                      delete: playbooks/delete.yaml
                  scaling_up:
                    type: steampunk.interfaces.scaling.ScaleUp
                  scaling_down:
                    type: steampunk.interfaces.scaling.ScaleDown
                  autoscaling:
                    operations:
                      retrieve_info:
                        description: Operation for autoscaling.
                        implementation: playbooks/retrieve_info.yaml
                      autoscale:
                        description: Operation for autoscaling.
                        implementation: playbooks/auto_scale.yaml
                        inputs:
                          min_size:
                            type: float
                            value: { get_property: [ autoscale, min_size ] }
                          max_size:
                            type: float
                            value: { get_property: [ autoscale, max_size ] }

              steampunk.nodes.ConfigureMonitoring:
                derived_from: tosca.nodes.Root
                interfaces:
                  Standard:
                    type: tosca.interfaces.node.lifecycle.Standard
                    operations:
                      configure:
                        implementation: playbooks/configure.yaml
                        inputs:
                          cpu_lower_bound:
                            type: float
                            value: { get_property: [ steampunk.policies.scaling.ScaleDown, cpu_lower_bound ] }
                          cpu_upper_bound:
                            type: float
                            value: { get_property: [ steampunk.policies.scaling.ScaleUp, cpu_upper_bound ] }

            interface_types:
              steampunk.interfaces.scaling.ScaleDown:
                derived_from: tosca.interfaces.Root
                operations:
                  scale_down:
                    inputs:
                      adjustment:
                        type: float
                        value: { get_property: [ steampunk.policies.scaling.ScaleDown, adjustment ] }
                    description: Operation for scaling down.
                    implementation: playbooks/scale_down.yaml

              steampunk.interfaces.scaling.ScaleUp:
                derived_from: tosca.interfaces.Root
                operations:
                  scale_up:
                    inputs:
                      adjustment:
                        type: float
                        value: { get_property: [ steampunk.policies.scaling.ScaleUp, adjustment ] }
                    description: Operation for scaling up.
                    implementation: playbooks/scale_up.yaml

            policy_types:
              steampunk.policies.scaling.ScaleDown:
                derived_from: tosca.policies.Scaling
                properties:
                  cpu_lower_bound:
                    description: The lower bound for the CPU
                    type: float
                    required: false
                    constraints:
                      - less_or_equal: 20.0
                  adjustment:
                    description: The amount by which to scale
                    type: integer
                    required: false
                    constraints:
                      - less_or_equal: -1
                targets: [ steampunk.nodes.VM, steampunk.nodes.ConfigureMonitoring ]
                triggers:
                  steampunk.triggers.scaling.ScaleDown:
                    description: A trigger for scaling down
                    event: scale_down_trigger
                    target_filter:
                      node: steampunk.nodes.VM
                    condition:
                      constraint:
                        - not:
                            - and:
                                - available_instances: [ { greater_than: 42 } ]
                                - available_space: [ { greater_than: 1000 } ]
                    action:
                      - call_operation:
                          operation: scaling_down.scale_down
                          inputs:
                            adjustment: { get_property: [ SELF, adjustment ] }

              steampunk.policies.scaling.ScaleUp:
                derived_from: tosca.policies.Scaling
                properties:
                  cpu_upper_bound:
                    description: The upper bound for the CPU
                    type: float
                    required: false
                    constraints:
                      - greater_or_equal: 80.0
                  adjustment:
                    description: The amount by which to scale
                    type: integer
                    required: false
                    constraints:
                      - greater_or_equal: 1
                targets: [ steampunk.nodes.VM, steampunk.nodes.ConfigureMonitoring ]
                triggers:
                  steampunk.triggers.scaling.ScaleUp:
                    description: A trigger for scaling up
                    event: scale_up_trigger
                    target_filter:
                      node: steampunk.nodes.VM
                    condition:
                      constraint:
                        - not:
                            - and:
                                - available_instances: [ { greater_than: 42 } ]
                                - available_space: [ { greater_than: 1000 } ]
                    action:
                      - call_operation:
                          operation: scaling_up.scale_up
                          inputs:
                            adjustment: { get_property: [ SELF, adjustment ] }

              steampunk.policies.scaling.AutoScale:
                derived_from: tosca.policies.Scaling
                properties:
                  min_size:
                    type: integer
                    description: The minimum number of instances
                    required: true
                    status: supported
                    constraints:
                      - greater_or_equal: 1
                  max_size:
                    type: integer
                    description: The maximum number of instances
                    required: true
                    status: supported
                    constraints:
                      - greater_or_equal: 10

            topology_template:
              node_templates:
                VM:
                  type: steampunk.nodes.VM

                ConfigureMonitoring:
                  type: steampunk.nodes.ConfigureMonitoring

              policies:
                - scale_down:
                    type: steampunk.policies.scaling.ScaleDown
                    properties:
                      cpu_lower_bound: 10
                      adjustment: 1

                - scale_up:
                    type: steampunk.policies.scaling.ScaleUp
                    properties:
                      cpu_upper_bound: 90
                      adjustment: 5

                - autoscale:
                    type: steampunk.policies.scaling.AutoScale
                    properties:
                      min_size: 3
                      max_size: 7
                    targets: [ VM ]
                    triggers:
                      steampunk.triggers.scaling.AutoScale:
                        description: A trigger for autoscaling
                        event: auto_scale_trigger
                        schedule:
                          start_time: 2020-04-08T21:59:43.10-06:00
                          end_time: 2022-04-08T21:59:43.10-06:00
                        target_filter:
                          node: VM
                          requirement: workstation
                          capability: host_capability
                        condition:
                          constraint:
                            - not:
                                - and:
                                    - available_instances: [ { greater_than: 42 } ]
                                    - available_space: [ { greater_than: 1000 } ]
                          period: 60 sec
                          evaluations: 2
                          method: average
                        action:
                          - call_operation: autoscaling.retrieve_info
                          - call_operation: autoscaling.autoscale
            """
        ))
        # language=yaml
        playbook = \
            """
            - hosts: all
              tasks:
                - name: Debug
                  debug:
                    msg: "Just testing."
            """
        pathlib.Path.mkdir(tmp_path / "playbooks")
        (tmp_path / "playbooks" / "create.yaml").write_text(yaml_text(playbook))
        (tmp_path / "playbooks" / "delete.yaml").write_text(yaml_text(playbook))
        (tmp_path / "playbooks" / "configure.yaml").write_text(yaml_text(playbook))
        (tmp_path / "playbooks" / "scale_up.yaml").write_text(yaml_text(playbook))
        (tmp_path / "playbooks" / "scale_down.yaml").write_text(yaml_text(playbook))
        (tmp_path / "playbooks" / "retrieve_info.yaml").write_text(yaml_text(playbook))
        (tmp_path / "playbooks" / "auto_scale.yaml").write_text(yaml_text(playbook))

        storage = Storage(tmp_path / pathlib.Path(".opera"))
        storage.write("service.yaml", "root_file")
        ast = tosca.load(tmp_path, name)
        template = ast.get_template({})
        template.instantiate(storage)
        yield template

    def test_count_policies_for_service_template(self, service_template):
        assert len(service_template.policies) == 3

    def test_count_policies_for_node(self, service_template):
        node_vm = service_template.find_node("VM")
        assert len(node_vm.policies) == 3

        node_monitoring = service_template.find_node("ConfigureMonitoring")
        assert len(node_monitoring.policies) == 2

    def test_find_policies_for_node(self, service_template):
        node_vm = service_template.find_node("VM")
        node_vm_policies = [policy.name for policy in node_vm.policies]

        assert "scale_down" in node_vm_policies
        assert "scale_up" in node_vm_policies
        assert "autoscale" in node_vm_policies

        node_monitoring = service_template.find_node("ConfigureMonitoring")
        node_monitoring_policies = [policy.name for policy in node_monitoring.policies]

        assert "scale_down" in node_monitoring_policies
        assert "scale_up" in node_monitoring_policies

    def test_find_policy_targets(self, service_template):
        node_vm = service_template.find_node("VM")
        node_vm_policy_targets = [policy.targets for policy in node_vm.policies]

        assert "VM" in node_vm_policy_targets[0]
        assert "VM" in node_vm_policy_targets[1]
        assert "VM" in node_vm_policy_targets[2]

    def test_find_policy_triggers(self, service_template):
        node_vm = service_template.find_node("VM")
        node_vm_policy_triggers = [policy.triggers for policy in node_vm.policies]

        assert "steampunk.triggers.scaling.ScaleDown" in node_vm_policy_triggers[0]
        assert "steampunk.triggers.scaling.ScaleUp" in node_vm_policy_triggers[1]
        assert "steampunk.triggers.scaling.AutoScale" in node_vm_policy_triggers[2]

    def test_find_policy_trigger_events(self, service_template):
        node_vm = service_template.find_node("VM")
        node_vm_policy_triggers = [policy.triggers for policy in node_vm.policies]

        assert node_vm_policy_triggers[0]["steampunk.triggers.scaling.ScaleDown"].event.data == "scale_down_trigger"
        assert node_vm_policy_triggers[1]["steampunk.triggers.scaling.ScaleUp"].event.data == "scale_up_trigger"
        assert node_vm_policy_triggers[2]["steampunk.triggers.scaling.AutoScale"].event.data == "auto_scale_trigger"

    def test_find_policy_trigger_target_filter(self, service_template):
        node_vm = service_template.find_node("VM")
        node_vm_policy_triggers = [policy.triggers for policy in node_vm.policies]

        assert node_vm_policy_triggers[0]["steampunk.triggers.scaling.ScaleDown"].target_filter[0] == "VM"
        assert node_vm_policy_triggers[1]["steampunk.triggers.scaling.ScaleUp"].target_filter[0] == "VM"
        assert node_vm_policy_triggers[2]["steampunk.triggers.scaling.AutoScale"].target_filter[0] == "VM"

    def test_find_policy_trigger_action(self, service_template):
        node_vm = service_template.find_node("VM")
        node_vm_policy_triggers = [policy.triggers for policy in node_vm.policies]

        interface1, operation1, _ = node_vm_policy_triggers[0]["steampunk.triggers.scaling.ScaleDown"].action[0]
        assert ("scaling_down", "scale_down") == (interface1, operation1)

        interface2, operation2, _ = node_vm_policy_triggers[1]["steampunk.triggers.scaling.ScaleUp"].action[0]
        assert ("scaling_up", "scale_up") == (interface2, operation2)

        interface3, operation3, _ = node_vm_policy_triggers[2]["steampunk.triggers.scaling.AutoScale"].action[0]
        assert ("autoscaling", "retrieve_info") == (interface3, operation3)

        interface3, operation3, _ = node_vm_policy_triggers[2]["steampunk.triggers.scaling.AutoScale"].action[1]
        assert ("autoscaling", "autoscale") == (interface3, operation3)

    def test_find_policy_properties(self, service_template):
        node_vm = service_template.find_node("VM")
        node_vm_policy_properties = [policy.properties for policy in node_vm.policies]

        assert "cpu_lower_bound" in node_vm_policy_properties[0]
        assert "adjustment" in node_vm_policy_properties[0]
        assert "cpu_upper_bound" in node_vm_policy_properties[1]
        assert "adjustment" in node_vm_policy_properties[1]
        assert "min_size" in node_vm_policy_properties[2]
        assert "max_size" in node_vm_policy_properties[2]

    def test_get_policy_properties(self, service_template):
        node_vm = service_template.find_node("VM")

        assert node_vm.get_property(("scale_down", "cpu_lower_bound")) == 10.0
        assert node_vm.get_property(("scale_down", "adjustment")) == 1

        assert node_vm.get_property(("scale_up", "cpu_upper_bound")) == 90.0
        assert node_vm.get_property(("scale_up", "adjustment")) == 5

        assert node_vm.get_property(("autoscale", "min_size")) == 3
        assert node_vm.get_property(("autoscale", "max_size")) == 7
