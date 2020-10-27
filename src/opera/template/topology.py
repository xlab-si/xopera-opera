import itertools

from opera.error import DataError
from opera.instance.topology import Topology as Instance


class Topology:
    def __init__(self, inputs, outputs, nodes, relationships):
        self.inputs = inputs
        self.outputs = outputs
        self.nodes = nodes
        self.relationships = relationships

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

    def instantiate(self, storage):
        return Instance(storage, itertools.chain.from_iterable(
            node.instantiate() for node in self.nodes.values()
        ))

    def get_outputs(self):
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
            raise DataError(
                "Node template or relationship template "
                "'{}' does not exist.".format(entity_name),
            )

        if node and relationship:
            if node.name == relationship.name:
                raise DataError(
                    "Node template and relationship template "
                    "'{}' should not have the same name.".format(entity_name),
                )

        if node:
            return node

        if relationship:
            return relationship

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
        # TODO(@tadeboro): Allow nested data access.
        if not isinstance(params, list):
            params = [params]

        if params[0] not in self.inputs:
            raise DataError("Invalid input: '{}'".format(params[0]))

        return self.inputs[params[0]].eval(self, params[0])

    def get_property(self, params):
        entity_name, *rest = params

        return self.find_node_or_relationship(entity_name).get_property(["SELF"] + rest)

    def get_attribute(self, params):
        entity_name, *rest = params
        return self.find_node_or_relationship(entity_name).get_attribute(["SELF"] + rest)

    def get_artifact(self, params):
        entity_name, *rest = params

        return self.find_node_or_relationship(entity_name).get_artifact(["SELF"] + rest)

    def concat(self, params, node=None):
        if not isinstance(params, list):
            raise DataError("Concat intrinsic function parameters '{}'"
                            " should be a list".format(params))

        return self.join([params], node)

    def join(self, params, node=None):
        if 1 <= len(params) <= 2:
            if not isinstance(params[0], list):
                raise DataError("Concat or join intrinsic function parameters "
                                "'{}' should be a list".format(params))

            string_value_expressions = params[0]
            delimiter = "" if len(params) == 1 else params[1]

            if not isinstance(delimiter, str):
                raise DataError(
                    "Delimiter: '{}' should be a string.".format(delimiter))

            values_to_join = []
            for param in string_value_expressions:
                if isinstance(param, dict):
                    param_dict_keys = list(param.keys())
                    if len(param_dict_keys) > 1:
                        raise DataError(
                            "Dict value expression for concat or join "
                            "function has too many keys: '{}'".format(param))

                    value_expression_name = param_dict_keys[0]
                    try:
                        entity = node if node else self
                        values_to_join.append(
                            getattr(entity, value_expression_name)(
                                param[value_expression_name]))
                    except Exception:
                        raise DataError(
                            "Invalid value expression for concat or join "
                            "function: '{}'".format(value_expression_name))
                elif isinstance(param, str):
                    values_to_join.append(param)
                else:
                    raise DataError(
                        "Invalid value for concat or join function function: "
                        "'{}'".format(param))

            return delimiter.join(values_to_join)
        else:
            raise DataError("Too many or too less parameters for: '{}'. Join "
                            "or concat intrinsic functions can only receive "
                            "one or two parameters.".format(params))

    def token(self, params):
        if isinstance(params, list) and len(params) == 3:
            string_with_tokens = params[0]
            string_of_token_chars = params[1]
            substring_index = params[2]

            if not isinstance(string_with_tokens, str):
                raise DataError(
                    "String with tokens: '{}' should be a string!".format(
                        string_with_tokens))

            if not isinstance(string_of_token_chars, str):
                raise DataError(
                    "String of token chars: '{}' should be a string!".format(
                        string_of_token_chars))

            if not isinstance(substring_index, int):
                raise DataError(
                    "Substring index: '{}' should be an integer!".format(
                        substring_index))

            if string_of_token_chars not in string_with_tokens:
                raise DataError(
                    "Token: '{}' is not present in string '{}'.".format(
                        string_of_token_chars, string_with_tokens))

            substrings = string_with_tokens.split(string_of_token_chars)

            if not 0 <= substring_index < len(substrings):
                raise DataError("Substring index '{}' for token function "
                                "does not exist.".format(substring_index))

            return substrings[substring_index]
        else:
            raise DataError(
                "Too many or too less parameters for: '{}'. Token intrinsic "
                "function requires exactly three parameters.".format(params))
