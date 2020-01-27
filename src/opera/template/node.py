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
