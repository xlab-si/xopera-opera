from typing import Optional

from opera_tosca_parser.parser.tosca.v_1_3.template.topology import Topology as Template

from opera.threading import NodeExecutor
from opera.constants import OperationHost
from opera.error import DataError
from .node import Node
from .relationship import Relationship


class Topology:  # pylint: disable=too-many-public-methods
    def __init__(self, template, storage=None):
        self.storage = storage
        self.nodes = {n.tosca_id: n for n in (Node.instantiate(node, self) for node in template.nodes.values())}
        self.relationships = {r.tosca_id: r for r in (Relationship.instantiate(relationship, self)
                              for relationship in template.relationships.values())}
        self.template = template

        for node in self.nodes.values():
            node.instantiate_relationships()
            if self.storage:
                node.read()

    def status(self):
        if any(node.deploying for node in self.nodes.values()):
            return "deploying"

        if all(node.deployed for node in self.nodes.values()):
            return "deployed"

        if any(node.undeploying for node in self.nodes.values()):
            return "undeploying"

        if all(node.undeployed for node in self.nodes.values()):
            return "undeployed"

        if any(node.error for node in self.nodes.values()):
            return "error"

        return "unknown"

    def validate(self, verbose, workdir, num_workers=None):
        # Currently, we are running a really stupid O(n^3) algorithm, but unless we get to the templates with
        # millions of node instances, we should be fine.
        with NodeExecutor(num_workers) as executor:
            do_validate = True
            while do_validate:
                for node in self.nodes.values():
                    if not node.validated and executor.can_submit(node.tosca_id):
                        executor.submit_operation(node.validate, node.tosca_id, verbose, workdir)
                do_validate = executor.wait_results()

    def deploy(self, verbose, workdir, num_workers=None):
        # Currently, we are running a really stupid O(n^3) algorithm, but unless we get to the templates with
        # millions of node instances, we should be fine.
        with NodeExecutor(num_workers) as executor:
            do_deploy = True
            while do_deploy:
                for node in self.nodes.values():
                    if (not node.deployed
                            and node.ready_for_deploy
                            and executor.can_submit(node.tosca_id)):
                        executor.submit_operation(node.deploy, node.tosca_id, verbose, workdir)
                do_deploy = executor.wait_results()

    def undeploy(self, verbose, workdir, num_workers=None):
        # Currently, we are running a really stupid O(n^3) algorithm, but unless we get to the templates with
        # millions of node instances, we should be fine.
        with NodeExecutor(num_workers) as executor:
            do_undeploy = True
            while do_undeploy:
                for node in self.nodes.values():
                    if (not node.undeployed
                            and node.ready_for_undeploy
                            and executor.can_submit(node.tosca_id)):
                        executor.submit_operation(node.undeploy, node.tosca_id, verbose, workdir)
                do_undeploy = executor.wait_results()

    def notify(self, verbose: bool, workdir: str, trigger_name_or_event: Optional[str],
               notification_file_contents: Optional[str], num_workers=1):
        # This will run selected interface operations on triggers from policies that have been applied to nodes.
        with NodeExecutor(num_workers) as executor:
            do_notify = True
            while do_notify:
                for node in self.nodes.values():
                    if not node.notified and executor.can_submit(node.tosca_id):
                        executor.submit_operation(node.notify, node.tosca_id, verbose, workdir, trigger_name_or_event,
                                                  notification_file_contents)
                do_notify = executor.wait_results()

    def write(self, data, instance_id):
        self.storage.write_json(data, "instances", instance_id)

    def write_all(self):
        for node in self.nodes.values():
            node.write()

    def read(self, instance_id):
        return self.storage.read_json("instances", instance_id)

    def set_storage(self, storage):
        self.storage = storage

    @staticmethod
    def instantiate(template: Template, storage=None):
        return Topology(template, storage)

    def find_node_or_relationship(self, entity_name):
        node = self.find_node(entity_name)
        relationship = self.find_relationship(entity_name)

        if not node and not relationship:
            raise DataError(f"Node template or relationship template '{entity_name}' does not exist.")

        if node and relationship:
            if node.name == relationship.name:
                raise DataError(
                    f"Node template and relationship template '{entity_name}' should not have the same name."
                )

        if node:
            return node
        if relationship:
            return relationship
        return None

    def find_node(self, node_name):
        if node_name not in self.template.nodes:
            return None

        return self.template.nodes[node_name].instance

    def find_relationship(self, relationship_name):
        if relationship_name not in self.template.relationships:
            return None

        return self.template.relationships[relationship_name].instance

    #
    # TOSCA functions
    #
    def get_input(self, params):
        # TODO: Allow nested data access.
        if not isinstance(params, list):
            params = [params]

        if params[0] not in self.template.inputs:
            raise DataError(f"Invalid input: '{params[0]}'")

        return self.template.inputs[params[0]].eval(self.template, params[0])

    def get_outputs(self) -> dict:
        return {
            k: dict(
                description=v["description"],
                value=v["value"].eval(self, "value"),
            ) for k, v in self.template.outputs.items()
        }

    def get_property(self, params):
        entity_name, *rest = params

        return self.find_node_or_relationship(entity_name).get_property([OperationHost.SELF.value] + rest)

    def get_attribute(self, params):
        entity_name, *rest = params
        return self.find_node_or_relationship(entity_name).get_attribute([OperationHost.SELF.value] + rest)

    def get_artifact(self, params):
        entity_name, *rest = params

        return self.find_node_or_relationship(entity_name).get_artifact([OperationHost.SELF.value] + rest)

    def concat(self, params, node=None):
        if not isinstance(params, list):
            raise DataError(f"Concat intrinsic function parameters '{params}' should be a list")

        return self.join([params], node)

    def join(self, params, node=None):
        if 1 <= len(params) <= 2:
            if not isinstance(params[0], list):
                raise DataError(f"Concat or join intrinsic function parameters '{params}' should be a list")

            string_value_expressions = params[0]
            delimiter = "" if len(params) == 1 else params[1]

            if not isinstance(delimiter, str):
                raise DataError(
                    f"Delimiter: '{delimiter}' should be a string.")

            values_to_join = []
            for param in string_value_expressions:
                if isinstance(param, dict):
                    param_dict_keys = list(param.keys())
                    if len(param_dict_keys) > 1:
                        raise DataError(
                            f"Dict value expression for concat or join function has too many keys: '{param}'"
                        )

                    value_expression_name = param_dict_keys[0]
                    try:
                        entity = node if node else self
                        values_to_join.append(
                            getattr(entity, value_expression_name)(
                                param[value_expression_name]))
                    except TypeError as e:
                        raise DataError(
                            f"Invalid value expression for concat or join function: '{value_expression_name}'"
                        ) from e
                elif isinstance(param, str):
                    values_to_join.append(param)
                else:
                    raise DataError(f"Invalid value for concat or join function function: '{param}'")

            return delimiter.join(values_to_join)
        else:
            raise DataError(
                f"Too many or too less parameters for: '{params}'. Join or concat intrinsic functions can only receive "
                f"one or two parameters."
            )

    @staticmethod
    def token(params):
        if isinstance(params, list) and len(params) == 3:
            string_with_tokens = params[0]
            string_of_token_chars = params[1]
            substring_index = params[2]

            if not isinstance(string_with_tokens, str):
                raise DataError(f"String with tokens: '{string_with_tokens}' should be a string!")

            if not isinstance(string_of_token_chars, str):
                raise DataError(f"String of token chars: '{string_of_token_chars}' should be a string!")

            if not isinstance(substring_index, int):
                raise DataError(f"Substring index: '{substring_index}' should be an integer!")

            if string_of_token_chars not in string_with_tokens:
                raise DataError(f"Token: '{string_of_token_chars}' is not present in string '{string_with_tokens}'.")

            substrings = string_with_tokens.split(string_of_token_chars)

            if not 0 <= substring_index < len(substrings):
                raise DataError(f"Substring index '{substring_index}' for token function does not exist.")

            return substrings[substring_index]
        else:
            raise DataError(
                f"Too many or too less parameters for: '{params}'. Token intrinsic function requires exactly three "
                f"parameters."
            )
