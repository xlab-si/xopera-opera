import itertools

from opera.constants import OperationHost
from opera.error import DataError
from opera.instance.topology import Topology as Instance


class Topology:
    def __init__(self, inputs, outputs, nodes, relationships, policies):
        self.inputs = inputs
        self.outputs = outputs
        self.nodes = nodes
        self.relationships = relationships
        self.policies = policies

        for node in self.nodes.values():
            node.topology = self

    def get_node(self, name):
        return self.nodes[name]

    def resolve_requirements(self):
        for node in self.nodes.values():
            node.resolve_requirements(self)
        self.resolve_relationships()

    def resolve_relationships(self):
        for node in self.nodes.values():
            for req in node.requirements:
                relationship = req.relationship
                if relationship.name in self.relationships.keys():
                    self.relationships[relationship.name] = relationship

    def resolve_policies(self):
        for node in self.nodes.values():
            for policy in self.policies:
                if policy.targets:
                    # apply policy to node if node name matches the target names that policy is limited to
                    if node.name in policy.targets.keys():
                        node.policies.append(policy)
                else:
                    # if we don't have target limits or filters apply policy to every node
                    node.policies.append(policy)

    def instantiate(self, storage):
        return Instance(storage, itertools.chain.from_iterable(node.instantiate() for node in self.nodes.values()))

    def get_outputs(self) -> dict:
        return {
            k: dict(
                description=v["description"],
                value=v["value"].eval(self, "value"),
            ) for k, v in self.outputs.items()
        }

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
        if node_name not in self.nodes:
            return None

        return self.nodes[node_name]

    def find_relationship(self, relationship_name):
        if relationship_name not in self.relationships:
            return None

        return self.relationships[relationship_name]

    #
    # TOSCA functions
    #
    def get_input(self, params):
        # TODO: Allow nested data access.
        if not isinstance(params, list):
            params = [params]

        if params[0] not in self.inputs:
            raise DataError(f"Invalid input: '{params[0]}'")

        return self.inputs[params[0]].eval(self, params[0])

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
