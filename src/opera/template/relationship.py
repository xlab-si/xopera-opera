from opera.error import DataError
from opera.instance.relationship import Relationship as Instance


class Relationship:
    def __init__(self, name, types, properties, attributes, interfaces):
        self.name = name
        self.types = types
        self.properties = properties
        self.attributes = attributes
        self.interfaces = interfaces

        # This will be set when the relationship is inserted into a topology
        self.topology = None

        # This will be set at instantiation time.
        self.instances = None

    def is_a(self, typ):
        return typ in self.types

    def instantiate(self, source, target):
        relationship_id = "{}--{}".format(source.tosca_id, target.tosca_id)
        self.instances = {relationship_id: Instance(self, relationship_id, source, target)}
        return self.instances.values()

    def run_operation(self, host, interface, operation, instance, verbose,
                      workdir):
        operation = self.interfaces[interface].operations.get(operation)
        if operation:
            return operation.run(host, instance, verbose, workdir)
        return True, {}, {}

    #
    # TOSCA functions
    #
    def get_property(self, params):
        host, prop, *rest = params

        if host == "HOST":
            raise DataError("HOST is not yet supported in opera.")
        if host != "SELF":
            raise DataError(
                "Property host should be set to 'SELF' which is the only "
                "valid value. This is needed to indicate that the property is "
                "referenced locally from something in the node itself."
            )

        # TODO(@tadeboro): Add support for nested property values once we
        # have data type support.
        if prop not in self.properties:
            raise DataError("Template has no '{}' property".format(prop))

        return self.properties[prop].eval(self, prop)

    def get_attribute(self, params):
        host, attr, *rest = params

        if host == "HOST":
            raise DataError("HOST is not yet supported in opera.")
        if host != "SELF":
            raise DataError(
                "Attribute host should be set to 'SELF' which is the only "
                "valid value. This is needed to indicate that the attribute "
                "is referenced locally from something in the node itself."
            )

        if attr not in self.attributes:
            raise DataError("Template has no '{}' attribute".format(attr))

        try:
            return self.attributes[attr].eval(self, attr)
        except DataError:
            pass

        if len(self.instances) != 1:
            raise DataError("Cannot get an attribute from multiple instances")

        return next(iter(self.instances.values())).get_attribute(params)

    def get_input(self, params):
        return self.topology.get_input(params)

    def map_attribute(self, params, value):
        host, prop, *rest = params

        if host not in ("SELF", "SOURCE", "TARGET"):
            raise DataError(
                "Attribute host should be set to 'SELF', 'SOURCE' or 'TARGET'."
            )

        if len(self.instances) != 1:
            raise DataError(
                "Mapping an attribute for multiple instances not supported")

        next(iter(self.instances.values())).map_attribute(params, value)
