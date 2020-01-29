import itertools

from opera.error import DataError
from opera.instance.topology import Topology as Instance


class Topology:
    def __init__(self, inputs, nodes):
        self.inputs = inputs
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
