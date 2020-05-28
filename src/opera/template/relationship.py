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

    def instantiate(self, source, target):
        relationship_id = "{}--{}".format(source.tosca_id, target.tosca_id)
        return Instance(self, relationship_id, source, target)

    def run_operation(self, host, interface, operation, instance):
        operation = self.interfaces[interface].operations.get(operation)
        if operation:
            return operation.run(host, instance)
        return True, {}, {}

    #
    # TOSCA functions
    #
    def get_property(self, params):
        host, prop, *rest = params

        if host != "SELF":
            raise DataError(
                "Accessing non-local stuff is bad. Fix your service template."
            )
        if host == "HOST":
            raise DataError("HOST is not yet supported in opera.")

        # TODO(@tadeboro): Add support for nested property values once we
        # have data type support.
        if prop not in self.properties:
            raise DataError("Template has no '{}' property".format(prop))
        return self.properties[prop].eval(self)

    def get_input(self, params):
        return self.topology.get_input(params)
