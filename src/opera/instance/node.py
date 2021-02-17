from typing import Optional

from opera.constants import StandardInterfaceOperation as Standard, ConfigureInterfaceOperation as Configure, \
    NodeState as State, OperationHost as Host
from opera.error import DataError
from opera.error import ToscaDeviationError
from opera.template.trigger import Trigger
from opera.threading import utils as thread_utils
from opera.value import Value
from .base import Base


class Node(Base):
    def __init__(self, template, instance_id):
        super().__init__(template, instance_id)

        self.in_edges = {}  # This gets filled by other instances for us.
        self.out_edges = {}  # This is what we fill during the linking phase.
        self.notified = False  # This indicates whether the node has been notified.

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
    def deployed(self):
        return self.state == State.STARTED

    @property
    def undeployed(self):
        return self.state == State.INITIAL

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

    def deploy(self, verbose, workdir):
        thread_utils.print_thread("  Deploying {}".format(self.tosca_id))

        self.set_state(State.CREATING)
        self.run_operation(Host.HOST, Standard.shorthand_name(), Standard.CREATE, verbose, workdir)
        self.set_state(State.CREATED)
        self.set_state(State.CONFIGURING)

        for requirement in set(r.name for r in self.template.requirements):
            for relationship in self.out_edges[requirement].values():
                relationship.run_operation(Host.SOURCE, Configure.shorthand_name(), Configure.PRE_CONFIGURE_SOURCE,
                                           verbose, workdir)

        for requirement_dependants in self.in_edges.values():
            for relationship in requirement_dependants.values():
                relationship.run_operation(Host.TARGET, Configure.shorthand_name(), Configure.PRE_CONFIGURE_TARGET,
                                           verbose, workdir)

        self.run_operation(Host.HOST, Standard.shorthand_name(), Standard.CONFIGURE, verbose, workdir)

        for requirement in set(r.name for r in self.template.requirements):
            for relationship in self.out_edges[requirement].values():
                relationship.run_operation(Host.SOURCE, Configure.shorthand_name(), Configure.POST_CONFIGURE_SOURCE,
                                           verbose, workdir)

        for requirement_dependants in self.in_edges.values():
            for relationship in requirement_dependants.values():
                relationship.run_operation(Host.TARGET, Configure.shorthand_name(), Configure.POST_CONFIGURE_TARGET,
                                           verbose, workdir)

        self.set_state(State.CONFIGURED)
        self.set_state(State.STARTING)
        self.run_operation(Host.HOST, Standard.shorthand_name(), Standard.START, verbose, workdir)
        self.set_state(State.STARTED)

        # TODO(@tadeboro): Execute various add hooks
        thread_utils.print_thread("  Deployment of {} complete".format(self.tosca_id))

    def undeploy(self, verbose, workdir):
        thread_utils.print_thread("  Undeploying {}".format(self.tosca_id))

        self.set_state(State.STOPPING)
        self.run_operation(Host.HOST, Standard.shorthand_name(), Standard.STOP, verbose, workdir)
        self.set_state(State.CONFIGURED)

        self.set_state(State.DELETING)
        self.run_operation(Host.HOST, Standard.shorthand_name(), Standard.DELETE, verbose, workdir)
        self.set_state(State.INITIAL)

        # TODO(@tadeboro): Execute various remove hooks

        self.reset_attributes()
        self.write()

        thread_utils.print_thread("  Undeployment of {} complete".format(self.tosca_id))

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
                        raise ToscaDeviationError("The input name: notification within the node: {} cannot be "
                                                  "used. It it reserved and holds the contents of notification "
                                                  "file. Please rename it.".format(self.template.name))

                    notification_value = Value(None, True, notification_file_contents)
                    operation.inputs.update({"notification": notification_value})

                self.run_operation(Host.HOST, interface_name, operation_name, verbose, workdir)

    def notify(self, verbose: bool, workdir: str, trigger_name_or_event: Optional[str],
               notification_file_contents: Optional[str]):
        thread_utils.print_thread("  Notifying {}".format(self.tosca_id))

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
                    thread_utils.print_thread("   Calling trigger {} with event {}".format(trigger_name, trigger.event))
                    self.invoke_trigger(verbose, workdir, trigger, notification_file_contents)
                    thread_utils.print_thread("   Calling trigger actions with event {} complete".format(trigger.event))

        self.notified = True
        thread_utils.print_thread("  Notification on {} complete".format(self.tosca_id))

    #
    # TOSCA functions
    #
    def get_attribute(self, params):
        host, attr, *rest = params

        if host == Host.HOST:
            raise DataError("{} is not yet supported in opera.".format(Host.HOST))
        if host != Host.SELF:
            raise DataError("Attribute host should be set to '{}' which is the only valid value. "
                            "This is needed to indicate that the attribute is referenced locally from something "
                            "in the node itself.".format(Host.SELF))

        # TODO(@tadeboro): Add support for nested attribute values once we
        # have data type support.
        if attr in self.attributes:
            return self.attributes[attr].eval(self, attr)

        # Check if there are capability and requirement with the same name.
        if attr in self.out_edges and attr in [c.name for c in self.template.capabilities]:
            raise DataError("There are capability and requirement with the same name: '{}'.".format(attr, ))

        # If we have no attribute, try searching for capability.
        capabilities = tuple(c for c in self.template.capabilities if c.name == attr)
        if len(capabilities) > 1:
            raise DataError("More than one capability is named '{}'.".format(attr, ))

        if len(capabilities) == 1 and capabilities[0].attributes and len(rest) != 0:
            return capabilities[0].attributes.get(rest[0]).data

        # If we have no attribute, try searching for requirement.
        relationships = self.out_edges.get(attr, {})
        if len(relationships) == 0:
            raise DataError("Cannot find attribute '{}'.".format(attr))
        if len(relationships) > 1:
            raise DataError("Targeting more than one instance via '{}'.".format(attr))
        return next(iter(relationships.values())).target.get_attribute([Host.SELF] + rest)

    def get_property(self, params):
        return self.template.get_property(params)

    def get_input(self, params):
        return self.template.get_input(params)

    def map_attribute(self, params, value):
        host, attr, *_ = params

        if host == Host.HOST:
            raise DataError("{} is not yet supported in opera.".format(Host.HOST))
        if host != Host.SELF:
            raise DataError("Attribute host should be set to '{}' which is the only valid value. "
                            "This is needed to indicate that the attribute is referenced locally from something "
                            "in the node itself.".format(Host.SELF))

        # TODO(@tadeboro): Add support for nested attribute values once we
        # have data type support.
        if attr not in self.attributes:
            raise DataError("Cannot find attribute '{}'.".format(attr))

        self.set_attribute(attr, value)

    def get_artifact(self, params):
        return self.template.get_artifact(params)

    def concat(self, params):
        return self.template.concat(params)

    def join(self, params):
        return self.template.join(params)

    def token(self, params):
        return self.template.token(params)
