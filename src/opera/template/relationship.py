from typing import Dict, Union

from opera.constants import OperationHost, StandardInterfaceOperation, ConfigureInterfaceOperation
from opera.error import DataError
from opera.instance.base import Base
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

    def run_operation(self,
                      host: OperationHost,
                      interface: str,
                      operation_type: Union[StandardInterfaceOperation, ConfigureInterfaceOperation],
                      instance: Base,
                      verbose: bool,
                      workdir: str):
        operation = self.interfaces[interface].operations.get(operation_type.value)
        if operation:
            return operation.run(host, instance, verbose, workdir)
        return True, {}, {}

    #
    # TOSCA functions
    #
    def get_property(self, params):
        host, prop, *_ = params

        if host == OperationHost.TARGET.value:
            raise DataError("{} is not yet supported in opera.".format(OperationHost.HOST.value))
        if host != OperationHost.SELF.value:
            raise DataError(
                "Property host should be set to '{}' which is the only valid value. This is needed to indicate that "
                "the property is referenced locally from something in the node itself. "
                "Was: {}".format(OperationHost.SELF.value, host)
            )

        # TODO(@tadeboro): Add support for nested property values once we
        # have data type support.
        if prop not in self.properties:
            raise DataError("Template has no '{}' property".format(prop))

        return self.properties[prop].eval(self, prop)

    def get_attribute(self, params):
        host, attr, *_ = params

        if host == OperationHost.HOST.value:
            raise DataError("{} is not yet supported in opera.".format(OperationHost.HOST.value))
        if host != OperationHost.SELF.value:
            raise DataError(
                "The attribute's 'host' should be set to '{}' which is the only valid value."
                "This is needed to indicate that the attribute is referenced locally from something in the node itself."
                " Was: {}".format(OperationHost.SELF.value, host)
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

        valid_hosts = [i.value for i in OperationHost]
        if host not in valid_hosts:
            raise DataError("The attribute's 'host' should be set to one of {}.".format(", ".join(valid_hosts)))

        if len(self.instances) != 1:
            raise DataError("Mapping an attribute for multiple instances not supported")

        next(iter(self.instances.values())).map_attribute(params, value)
