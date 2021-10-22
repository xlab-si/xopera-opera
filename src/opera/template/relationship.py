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
        relationship_id = f"{source.tosca_id}--{target.tosca_id}"
        self.instances = {relationship_id: Instance(self, relationship_id, source, target)}
        return self.instances.values()

    def run_operation(self,
                      host: OperationHost,
                      interface: str,
                      operation_type: Union[StandardInterfaceOperation, ConfigureInterfaceOperation],
                      instance: Base,
                      verbose: bool,
                      workdir: str,
                      validate: bool = False):
        operation = self.interfaces[interface].operations.get(operation_type.value)
        if operation:
            return operation.run(host, instance, verbose, workdir, validate)
        return True, {}, {}

    #
    # TOSCA functions
    #
    def get_property(self, params):
        host, prop, *_ = params

        if host == OperationHost.SELF.value:
            # TODO: Add support for nested property values.
            if prop not in self.properties:
                raise DataError(f"Template has no '{prop}' attribute")
            return self.properties[prop].eval(self, prop)
        elif host == OperationHost.HOST.value:
            raise DataError(f"{host} keyword can be only used within node template context.")
        else:
            # try to find the property within the TOSCA nodes
            for node in self.topology.nodes.values():
                if host == node.name or host in node.types:
                    # TODO: Add support for nested property values.
                    if prop in node.properties:
                        return node.properties[prop].eval(self, prop)
            # try to find the property within the TOSCA relationships
            for rel in self.topology.relationships.values():
                if host == rel.name or host in rel.types:
                    # TODO: Add support for nested property values.
                    if prop in rel.properties:
                        return rel.properties[prop].eval(self, prop)

            raise DataError(
                f"We were unable to find the property: {prop} within the specified modelable entity or keyname: "
                f"{host} for node: {self.name}. The valid entities to get properties from are currently TOSCA nodes, "
                f"relationships and policies. But the best practice is that the property host is set to "
                f"'{OperationHost.SELF.value}'. This indicates that the property is referenced locally from something "
                f"in the relationship itself."
            )

    def get_attribute(self, params):
        if len(self.instances) != 1:
            raise DataError("Cannot get an attribute from zero or multiple instances")

        return next(iter(self.instances.values())).get_attribute(params)

    def get_input(self, params):
        return self.topology.get_input(params)

    def map_attribute(self, params, value):
        if len(self.instances) != 1:
            raise DataError("Mapping an attribute for zero or multiple instances not supported")

        next(iter(self.instances.values())).map_attribute(params, value)
