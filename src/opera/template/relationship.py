from opera.error import DataError
from opera.instance.relationship import Relationship as Instance

class Relationship:
    def __init__(self, name, types, properties, attributes, interfaces):
        self.name = name
        self.types = types
        self.properties = properties
        self.attributes = attributes
        self.interfaces = interfaces

    def is_a(self, typ):
        return typ in self.types