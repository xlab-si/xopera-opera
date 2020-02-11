import itertools

from opera.error import DataError
from opera.instance.topology import Topology as Instance


class Topology:
    def __init__(self, inputs, outputs, nodes):
        self.inputs = inputs
        self.outputs = outputs
        self.nodes = nodes

        for node in self.nodes.values():
            node.topology = self

    def get_node(self, name):
        return self.nodes[name]

    def resolve_requirements(self):
        for node in self.nodes.values():
            node.resolve_requirements(self)

    def instantiate(self, storage):
        return Instance(storage, itertools.chain.from_iterable(
            node.instantiate() for node in self.nodes.values()
        ))

    def get_outputs(self):
        return {
            k: dict(
                description=v["description"],
                value=v["value"].eval(self),
            ) for k, v in self.outputs.items()
        }

    def find_node(self, node_name):
        if node_name not in self.nodes:
            raise DataError(
                "Node template '{}' does not exist.".format(node_name),
            )

        return self.nodes[node_name]

    #
    # TOSCA functions
    #
    def get_input(self, params):
        # TODO(@tadeboro): Allow nested data access.
        if not isinstance(params, list):
            params = [params]

        if params[0] not in self.inputs:
            raise DataError("Invalid input: '{}'".format(params[0]))

        return self.inputs[params[0]].eval(self)

    def get_property(self, params):
        node_name, *rest = params

        return self.find_node(node_name).get_property(["SELF"] + rest)

    def get_attribute(self, params):
        node_name, *rest = params

        return self.find_node(node_name).get_attribute(["SELF"] + rest)
