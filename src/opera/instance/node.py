from typing import Optional

from opera.constants import StandardInterfaceOperation, ConfigureInterfaceOperation, NodeState, OperationHost
from opera.error import DataError
from opera.error import ToscaDeviationError
from opera.template.trigger import Trigger
from opera.threading import utils as thread_utils
from opera.value import Value
from .base import Base


class Node(Base):  # pylint: disable=too-many-public-methods
    def __init__(self, template, instance_id):
        super().__init__(template, instance_id)

        self.in_edges = {}  # This gets filled by other instances for us.
        self.out_edges = {}  # This is what we fill during the linking phase.
        self.notified = False  # This indicates whether the node has been notified.
        self.validated = False  # This indicates whether the node has been validated.

    def instantiate_relationships(self):
        if not self.topology:
            raise AssertionError("Cannot instantiate relationships")

        for requirement in self.template.requirements:
            rname = requirement.name
            self.out_edges[rname] = self.out_edges.get(rname, {})

            for target in requirement.target.instances.values():
                target.in_edges[rname] = target.in_edges.get(rname, {})

                rel_instances = requirement.relationship.instantiate(self, target)
                for rel in rel_instances:
                    rel.topology = self.topology
                    self.out_edges[rname][target.tosca_id] = rel
                    target.in_edges[rname][self.tosca_id] = rel
                    target.in_edges[rname][self.tosca_id] = rel
                    rel.read()

    @property
    def deploying(self):
        return self.state in (NodeState.CREATING, NodeState.CREATED, NodeState.CONFIGURING, NodeState.STARTING)

    @property
    def deployed(self):
        return self.state == NodeState.STARTED

    @property
    def undeploying(self):
        return self.state in (NodeState.STOPPING, NodeState.DELETING)

    @property
    def undeployed(self):
        return self.state == NodeState.INITIAL

    @property
    def error(self):
        return self.state == NodeState.ERROR

    @property
    def ready_for_deploy(self):
        return all(
            relationship.target.deployed
            for requirement_relationships in self.out_edges.values()
            for relationship in requirement_relationships.values()
        )

    @property
    def ready_for_undeploy(self):
        return all(
            relationship.source.undeployed
            for requirement_relationships in self.in_edges.values()
            for relationship in requirement_relationships.values()
        )

    def get_host(self):
        # Try to transitively find a HostedOn requirement and resort to
        # localhost if nothing suitable is found.
        return self.template.get_host() or "localhost"

    def _configure_requirements(self,
                                source_operation: ConfigureInterfaceOperation,
                                target_operation: ConfigureInterfaceOperation,
                                verbose: bool, workdir: str,
                                validate: bool = False):
        for requirement in set(r.name for r in self.template.requirements):
            for relationship in self.out_edges[requirement].values():
                relationship.run_operation(OperationHost.SOURCE, ConfigureInterfaceOperation.shorthand_name(),
                                           source_operation, verbose, workdir, validate)

        for requirement_dependants in self.in_edges.values():
            for relationship in requirement_dependants.values():
                relationship.run_operation(OperationHost.TARGET, ConfigureInterfaceOperation.shorthand_name(),
                                           target_operation, verbose, workdir, validate)

    def validate(self, verbose, workdir):
        thread_utils.print_thread(f"  Validating {self.tosca_id}")

        # validate node's deployment
        self.run_operation(OperationHost.HOST, StandardInterfaceOperation.shorthand_name(),
                           StandardInterfaceOperation.CREATE, verbose, workdir, True)
        self._configure_requirements(ConfigureInterfaceOperation.PRE_CONFIGURE_SOURCE,
                                     ConfigureInterfaceOperation.PRE_CONFIGURE_TARGET, verbose, workdir, True)
        self.run_operation(OperationHost.HOST,
                           StandardInterfaceOperation.shorthand_name(),
                           StandardInterfaceOperation.CONFIGURE, verbose, workdir, True)
        self._configure_requirements(ConfigureInterfaceOperation.POST_CONFIGURE_SOURCE,
                                     ConfigureInterfaceOperation.POST_CONFIGURE_TARGET, verbose, workdir, True)
        self.run_operation(OperationHost.HOST, StandardInterfaceOperation.shorthand_name(),
                           StandardInterfaceOperation.START, verbose, workdir, True)

        # validate node's undeployment
        self.run_operation(OperationHost.HOST, StandardInterfaceOperation.shorthand_name(),
                           StandardInterfaceOperation.STOP, verbose, workdir, True)
        self.run_operation(OperationHost.HOST, StandardInterfaceOperation.shorthand_name(),
                           StandardInterfaceOperation.DELETE, verbose, workdir, True)
        self.reset_attributes()
        self.write()

        self.validated = True
        thread_utils.print_thread(f"  Validation of {self.tosca_id} complete")

    def deploy(self, verbose, workdir):
        thread_utils.print_thread(f"  Deploying {self.tosca_id}")

        self.set_state(NodeState.CREATING)
        self.run_operation(OperationHost.HOST, StandardInterfaceOperation.shorthand_name(),
                           StandardInterfaceOperation.CREATE, verbose, workdir)
        self.set_state(NodeState.CREATED)
        self.set_state(NodeState.CONFIGURING)

        self._configure_requirements(ConfigureInterfaceOperation.PRE_CONFIGURE_SOURCE,
                                     ConfigureInterfaceOperation.PRE_CONFIGURE_TARGET,
                                     verbose, workdir)

        self.run_operation(OperationHost.HOST,
                           StandardInterfaceOperation.shorthand_name(),
                           StandardInterfaceOperation.CONFIGURE,
                           verbose, workdir)

        self._configure_requirements(ConfigureInterfaceOperation.POST_CONFIGURE_SOURCE,
                                     ConfigureInterfaceOperation.POST_CONFIGURE_TARGET,
                                     verbose, workdir)

        self.set_state(NodeState.CONFIGURED)
        self.set_state(NodeState.STARTING)
        self.run_operation(OperationHost.HOST, StandardInterfaceOperation.shorthand_name(),
                           StandardInterfaceOperation.START, verbose, workdir)
        self.set_state(NodeState.STARTED)

        # TODO: Execute various add hooks
        thread_utils.print_thread(f"  Deployment of {self.tosca_id} complete")

    def undeploy(self, verbose, workdir):
        thread_utils.print_thread(f"  Undeploying {self.tosca_id}")

        self.set_state(NodeState.STOPPING)
        self.run_operation(OperationHost.HOST, StandardInterfaceOperation.shorthand_name(),
                           StandardInterfaceOperation.STOP, verbose, workdir)
        self.set_state(NodeState.CONFIGURED)

        self.set_state(NodeState.DELETING)
        self.run_operation(OperationHost.HOST, StandardInterfaceOperation.shorthand_name(),
                           StandardInterfaceOperation.DELETE, verbose, workdir)
        self.set_state(NodeState.INITIAL)

        # TODO: Execute various remove hooks

        self.reset_attributes()
        self.write()

        thread_utils.print_thread(f"  Undeployment of {self.tosca_id} complete")

    def invoke_trigger(self, verbose: bool, workdir: str, trigger: Trigger,
                       notification_file_contents: Optional[str]):
        for interface_name, operation_name, _ in trigger.action:
            # get node's interface and interface operations that are referenced in a trigger action
            interface = self.template.interfaces.get(interface_name, None)
            operation = interface.operations.get(operation_name, None) if interface else None

            if interface is not None and operation is not None:
                if notification_file_contents:
                    # add notification file contents to operation inputs that are exposed in the executor
                    if "notification" in operation.inputs:
                        raise ToscaDeviationError(
                            f"The input name: notification within the node: {self.template.name} cannot be used. It it "
                            f"reserved and holds the contents of notification file. Please rename it."
                        )

                    notification_value = Value(None, True, notification_file_contents)
                    operation.inputs.update({"notification": notification_value})

                self.run_operation(OperationHost.HOST, interface_name, operation_name, verbose, workdir)

    def notify(self, verbose: bool, workdir: str, trigger_name_or_event: Optional[str],
               notification_file_contents: Optional[str]):
        thread_utils.print_thread(f"  Notifying {self.tosca_id}")

        for policy in self.template.policies:
            for trigger_name, trigger in policy.triggers.items():
                # break here if trigger is not targeting this node
                if trigger.target_filter and trigger.target_filter[0] != self.template.name:
                    break

                invoke_trigger = True
                if trigger_name_or_event is not None and trigger_name_or_event not in (trigger_name,
                                                                                       trigger.event.data):
                    invoke_trigger = False

                # invoke the chosen trigger only if it contains any actions
                if invoke_trigger and trigger.action:
                    thread_utils.print_thread(f"   Calling trigger {trigger_name} with event {trigger.event}")
                    self.invoke_trigger(verbose, workdir, trigger, notification_file_contents)
                    thread_utils.print_thread(f"   Calling trigger actions with event {trigger.event} complete")

        self.notified = True
        thread_utils.print_thread(f"  Notification on {self.tosca_id} complete")

    #
    # TOSCA functions
    #
    def get_attribute(self, params):
        host, attr, *rest = params

        if host == OperationHost.SELF.value:
            # TODO: Add support for nested attribute values once we have data type support.
            if attr in self.attributes:
                return self.attributes[attr].eval(self, attr)

            # Check if there are capability and requirement with the same name.
            if attr in self.out_edges and attr in [c.name for c in self.template.capabilities]:
                raise DataError(f"There are capability and requirement with the same name: '{attr}'.")

            # If we have no attribute, try searching for capability.
            capabilities = tuple(c for c in self.template.capabilities if c.name == attr)
            if len(capabilities) > 1:
                raise DataError(f"More than one capability is named '{attr}'.")

            if len(capabilities) == 1 and capabilities[0].attributes and len(rest) != 0:
                return capabilities[0].attributes.get(rest[0]).data

            # If we have no attribute, try searching for requirement.
            relationships = self.out_edges.get(attr, {})
            if len(relationships) == 0:
                raise DataError(f"Cannot find attribute '{attr}' among {', '.join(self.out_edges.keys())}.")
            if len(relationships) > 1:
                raise DataError(f"Targeting more than one instance via '{attr}'.")

            return next(iter(relationships.values())).target.get_attribute([OperationHost.SELF.value] + rest)
        elif host == OperationHost.HOST.value:
            for req in self.template.requirements:
                # get value from the node that hosts the node as identified by its HostedOn relationship
                if "tosca.relationships.HostedOn" in req.relationship.types:
                    # TODO: Add support for nested attribute values.
                    if req.target and attr in req.target.attributes:
                        return req.target.attributes[attr].eval(self, attr)

            raise DataError(
                f"We were unable to find the attribute: {attr} specified with keyname: {host} for node: "
                f"{self.template.name}. Check if the node is connected to its host with tosca.relationships.HostedOn "
                f"relationship."
            )
        elif host in (OperationHost.SOURCE.value, OperationHost.TARGET.value):
            raise DataError(f"{host} keyword can be only used within relationship template context.")
        else:
            # try to find the attribute within the TOSCA nodes
            for node in self.template.topology.nodes.values():
                if host == node.name or host in node.types:
                    # TODO: Add support for nested attribute values.
                    if attr in node.attributes:
                        return node.attributes[attr].eval(self, attr)
            # try to find the attribute within the TOSCA relationships
            for rel in self.template.topology.relationships.values():
                if host == rel.name or host in rel.types:
                    # TODO: Add support for nested attribute values.
                    if attr in rel.attributes:
                        return rel.attributes[attr].eval(self, attr)

            raise DataError(
                f"We were unable to find the attribute: {attr} within the specified modelable entity or keyname: "
                f"{host} for node: {self.template.name}. The valid entities to get attributes from are currently TOSCA "
                f"nodes and relationships. But the best practice is that the attribute host is set to "
                f"'{OperationHost.SELF.value}'. This indicates that the attribute is referenced locally from something "
                f"in the node itself."
            )

    def get_property(self, params):
        return self.template.get_property(params)

    def get_input(self, params):
        return self.template.get_input(params)

    def map_attribute(self, params, value):
        host, attr, *rest = params

        if host != OperationHost.SELF.value:
            raise DataError(
                f"Invalid attribute host for attribute mapping: {host} for node: {self.template.name}. For operation "
                f"outputs in interfaces on node templates, the only allowed keyname is: {OperationHost.SELF.value}. "
                f"This is because the output values must always be stored into attributes that belong to the node "
                f"template that has the interface for which the output values are returned."
            )

        attribute_mapped = False
        # TODO: Add support for nested attribute values once we have data type support.
        if attr in self.attributes:
            self.set_attribute(attr, value)
            attribute_mapped = True

        # If we have no attribute, try searching for capability.
        capabilities = tuple(c for c in self.template.capabilities if c.name == attr)
        if len(capabilities) > 1:
            raise DataError(f"More than one capability is named '{attr}'.")

        if len(capabilities) == 1 and capabilities[0].attributes and len(rest) != 0:
            if rest[0] in capabilities[0].attributes:
                capabilities[0].attributes[rest[0]] = value
                attribute_mapped = True

        if not attribute_mapped:
            raise DataError(f"Cannot find attribute '{attr}' among {', '.join(self.attributes.keys())}.")

    def get_artifact(self, params):
        return self.template.get_artifact(params)

    def concat(self, params):
        return self.template.concat(params)

    def join(self, params):
        return self.template.join(params)

    def token(self, params):
        return self.template.token(params)
