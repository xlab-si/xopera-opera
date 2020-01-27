from opera.error import DataError
from opera.instance.node import Node as Instance


class Node:
    def __init__(
            self,
            name,
            types,
            properties,
            attributes,
            requirements,
            interfaces,
    ):
        self.name = name
        self.types = types
        self.properties = properties
        self.attributes = attributes
        self.requirements = requirements
        self.interfaces = interfaces

        # This will be set at instantiation time.
        self.instances = None

    def resolve_requirements(self, topology):
        for r in self.requirements:
            r.resolve(topology)

    def is_a(self, typ):
        return typ in self.types

    def instantiate(self):
        # NOTE(@tadeboro): This is where we should handle multiple instances.
        # At the moment, we simply create one instance per node template. But
        # the algorithm is fully prepared for multiple instances.
        node_id = self.name + "_0"
        self.instances = {node_id: Instance(self, node_id)}
        return self.instances.values()
