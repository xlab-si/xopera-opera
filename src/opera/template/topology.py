import itertools

from opera.error import DataError
from opera.instance.topology import Topology as Instance


class Topology:
    def __init__(self, nodes):
        self.nodes = nodes

    def get_node(self, name):
        return self.nodes[name]

    def resolve_requirements(self):
        for node in self.nodes.values():
            node.resolve_requirements(self)

    def instantiate(self, storage):
        return Instance(storage, itertools.chain.from_iterable(
            node.instantiate() for node in self.nodes.values()
        ))
