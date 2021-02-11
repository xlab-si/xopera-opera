from typing import Dict

from opera.constants import OperationHost as Host
from opera.error import DataError
from opera.instance.relationship import Relationship as Instance
from opera.template.topology import Topology


class Relationship:
    def __init__(self, name, types, properties, attributes, interfaces):
        self.name = name
        self.types = types
        self.properties = properties
        self.attributes = attributes
        self.interfaces = interfaces

        # This will be set when the relationship is inserted into a topology
        self.topology: Topology = None

        # This will be set at instantiation time.
        self.instances: Dict = None  # type: ignore

    def is_a(self, typ):
        return typ in self.types

    def instantiate(self, source, target):
        relationship_id = "{}--{}".format(source.tosca_id, target.tosca_id)
        self.instances = {relationship_id: Instance(self, relationship_id, source, target)}
        return self.instances.values()

    def run_operation(self, host, interface, operation, instance, verbose, workdir):
        operation = self.interfaces[interface].operations.get(operation)
        if operation:
            return operation.run(host, instance, verbose, workdir)
        return True, {}, {}

    #
    # TOSCA functions
    #
    def get_property(self, params):
        host, prop, *_ = params

        if host == Host.TARGET:
            raise DataError("{} is not yet supported in opera.".format(Host.HOST))
        if host != Host.SELF:
            raise DataError(
                "Property host should be set to '{}' which is the only valid value. This is needed to indicate that "
                "the property is referenced locally from something in the node itself.".format(Host.SELF)
            )

        # TODO(@tadeboro): Add support for nested property values once we
        # have data type support.
        if prop not in self.properties:
            raise DataError("Template has no '{}' property".format(prop))

        return self.properties[prop].eval(self, prop)

    def get_attribute(self, params):
        host, attr, *_ = params

        if host == Host.HOST:
            raise DataError("{} is not yet supported in opera.".format(Host.HOST))
        if host != Host.SELF:
            raise DataError(
                "Attribute host should be set to '{}' which is the only valid value. This is needed to indicate that "
                "the attribute is referenced locally from something in the node itself.".format(Host.SELF)
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
        host, *_ = params

        valid_hosts = [i.value for i in Host]
        if host not in valid_hosts:
            raise DataError("Attribute host should be set to one of {}.".format(", ".join(valid_hosts)))

        if len(self.instances) != 1:
            raise DataError("Mapping an attribute for multiple instances not supported")

        next(iter(self.instances.values())).map_attribute(params, value)
