from typing import Optional, Dict, Any, Tuple, List as TypingList

from opera.template.node import Node
from opera.template.operation import Operation
from opera.template.policy import Policy
from opera.template.trigger import Trigger
from .collector_mixin import CollectorMixin  # type: ignore
from .trigger_definition import TriggerDefinition
from ..entity import Entity
from ..list import List
from ..map import Map
from ..reference import Reference, ReferenceXOR
from ..string import String
from ..void import Void


class PolicyDefinition(CollectorMixin, Entity):
    ATTRS = dict(
        type=Reference("policy_types"),
        description=String,
        metadata=Map(String),
        properties=Map(Void),
        targets=List(ReferenceXOR(("topology_template", "node_templates"), ("topology_template", "groups"))),
        triggers=Map(TriggerDefinition),
    )
    REQUIRED = {"type"}

    def get_template(self, name: str, service_ast: Dict[str, Any], nodes: Dict[str, Node]):
        # targets will be used also for collecting triggers so retrieve them here only once
        targets = self.collect_targets(service_ast)

        policy = Policy(
            name=name,
            types=self.collect_types(service_ast),
            properties=self.collect_properties(service_ast),
            targets=targets,
            triggers=self.collect_triggers(service_ast, targets, nodes)
        )

        policy.resolve_targets(nodes)
        return policy

    # the next function is not part of the CollectorMixin because targets are policy only thing
    def collect_targets(self, service_ast: Dict[str, Any]):
        typ = self.type.resolve_reference(service_ast)
        definitions = typ.collect_target_definitions(service_ast)
        assignments = {target.data: target for target in self.get("targets", [])}

        duplicate_targets = set(assignments.keys()).intersection(definitions.keys())
        if duplicate_targets:
            for duplicate in duplicate_targets:
                definitions.pop(duplicate)

        definitions.update(assignments)

        return {
            name: (assignments.get(name) or definition).resolve_reference(service_ast)
            for name, definition in definitions.items()
        }

    # the next function is not part of the CollectorMixin because triggers are policy only thing
    def collect_trigger_action_from_interfaces(self, targeted_nodes: Dict[str, Node],
                                               call_operation_name: Optional[str],
                                               action: Dict[str, Any]) -> Optional[Tuple[str, str, Operation]]:
        collected_action = None
        actions_found = 0
        for _, target_node in targeted_nodes.items():
            # loop through interfaces from targeted nodes
            for interface_name, interface in target_node.interfaces.items():
                # loop through interface operations from targeted nodes
                for operation_name, operation in interface.operations.items():
                    # find the corresponding node's interface operation
                    if str(interface_name) + "." + str(operation_name) == str(call_operation_name):
                        actions_found += 1

                        # override the operation inputs with inputs from trigger's activity definition
                        operation.inputs = {
                            k: [s.data for s in v.data]
                            for k, v in action.get("inputs", {}).items()
                        }

                        collected_action = (interface_name, operation_name, operation)
                        break

        if actions_found == 0:
            self.abort("Trigger action: {} from call_operation does not belong to any node interface. Make "
                       "sure that you have referenced it correctly (as "
                       "<interface_sub_name>.<operation_sub_name>, where interface_sub_name is the "
                       "interface name and the operation_sub_name is the name of the operation within this "
                       "interface). The node that you're targeting with interface operation also has to be "
                       "used in topology_template/node_templates section."
                       .format(call_operation_name), self.loc)
        elif actions_found > 1:
            self.abort("Found duplicated trigger actions: {} from call_operation. It seems that the "
                       "operation with the same name belongs to two different node types/templates. "
                       "".format(call_operation_name), self.loc)

        return collected_action

    # the next function is not part of the CollectorMixin because triggers are policy only thing
    def collect_trigger_target_nodes(self, target_filter: Optional[Tuple[str, Any]], nodes: Dict[str, Node],
                                     policy_targets: Dict[str, Any]) -> Dict[str, Node]:
        # pylint: disable=no-self-use
        targeted_nodes = dict()
        if target_filter:
            # if target node filter is applied collect just one targeted node from it
            for node_name, node in nodes.items():
                if node_name == target_filter[0] or node.types[0] == target_filter[0]:
                    targeted_nodes[node_name] = node
                    break
        elif policy_targets:
            # if target_filter is not present collect target nodes from policy's targets
            for node_name, node in nodes.items():
                for policy_target_name, _ in policy_targets.items():
                    if policy_target_name in (node_name, node.types[0]):
                        targeted_nodes[node_name] = node
        else:
            # if we don't have any target node limits take all template's nodes into account
            targeted_nodes = nodes

        return targeted_nodes

    # the next function is not part of the CollectorMixin because triggers are policy only thing
    def collect_trigger_actions(self, definition: Dict[str, Any],
                                target_filter: Optional[Tuple[str, Any]], nodes: Dict[str, Node],
                                policy_targets: Dict[str, Any]) -> TypingList[Tuple[str, str, Operation]]:
        actions = []
        action_definitions = definition.get("action", [])
        for action in action_definitions:
            # TODO: implement support for other types of trigger activity definitions.
            if list(action)[0] != "call_operation":
                self.abort("Unsupported trigger activity definitions: {}. Only call_operation is supported."
                           .format(list(action)[0]), self.loc)
            else:
                # collect connected node interface operations
                call_operation = action.get("call_operation", None)
                call_operation_name = None
                # handle short call_operation notation
                if isinstance(call_operation.data, str):
                    call_operation_name = call_operation.data
                # handle extended call_operation notation
                elif isinstance(call_operation.data, dict):
                    call_operation_name = call_operation.data.get("operation", None)
                else:
                    self.abort("Invalid call operation activity definition type: {}."
                               .format(type(call_operation.data, )), self.loc)

                # having no operation name should never happen but to be completely sure we can also check here
                if not call_operation_name:
                    self.abort("Missing required name for call_operation activity definition.", self.loc)

                # find Node objects that we are targeting with trigger action
                targeted_nodes = self.collect_trigger_target_nodes(target_filter, nodes, policy_targets)

                # collect actions (interface operations) from targeted nodes
                collected_action = self.collect_trigger_action_from_interfaces(targeted_nodes, call_operation_name,
                                                                               action)
                if collected_action:
                    actions.append(collected_action)

        return actions

    # the next function is not part of the CollectorMixin because triggers are policy only thing
    def collect_triggers(self, service_ast: Dict[str, Any], policy_targets: Dict[str, Any], nodes: Dict[str, Node]):
        # pylint: disable=too-many-locals
        typ = self.type.resolve_reference(service_ast)
        definitions = typ.collect_trigger_definitions(service_ast)
        assignments = self.get("triggers", {})

        duplicate_triggers = set(assignments.keys()).intersection(definitions.keys())
        if duplicate_triggers:
            for duplicate in duplicate_triggers:
                definitions.pop(duplicate)

        definitions.update(assignments)

        # TODO: optimize this code which is now nasty with a lot of parsing, looping and everything else.
        triggers = dict()
        for name, definition in definitions.items():
            # collect and resolve target filter definition
            target_filter = None
            target_filter_definitions = definition.get("target_filter", None)
            if target_filter_definitions:
                target_node = target_filter_definitions.get("node", None)
                if target_node:
                    # resolve node reference and set target_filter
                    target_filter = (target_node.data, target_node.resolve_reference(service_ast))
                else:
                    self.abort("Cannot obtain node from target_filter.", self.loc)

            # check if target_filter also matches one node reference from policy's targets
            if target_filter and policy_targets and target_filter[0] not in list(policy_targets):
                self.abort("The node reference: {} from policy trigger's target_filter should be also present in "
                           "policy's targets.".format(target_filter[0]), self.loc)

            # collect action definitions
            actions = self.collect_trigger_actions(definition, target_filter, nodes, policy_targets)

            trigger = Trigger(name=name,
                              event=definition.get("event", None),
                              target_filter=target_filter,
                              condition=definition.get("condition", None),
                              action=actions)

            trigger.resolve_event_filter(nodes)
            triggers[name] = trigger

        return triggers
