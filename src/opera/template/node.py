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

        # This will be set when the node is inserted into a topology
        self.topology = None

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

    def get_host(self):
        # TODO(@tadeboro): Properly handle situations where multiple hosts are
        # available.

        # 1. Scan requirements for direct compute host and return one.
        # 2. Scan requirements for indirect compute host and return one.
        # 3. Default to localhost.

        host = next((
            r.target
            for r in self.requirements
            if r.relationship.is_a("tosca.relationships.HostedOn")
            and r.target.is_a("tosca.nodes.Compute")
        ), None)
        if host:
            instance = next(iter(host.instances.values()))
            return instance.attributes["public_address"].eval(self)

        host = next((
            r.target.get_host()
            for r in self.requirements
            if r.relationship.is_a("tosca.relationships.HostedOn")
        ), None)

        return host or "localhost"

    def run_operation(self, host, interface, operation, instance):
        operation = self.interfaces[interface].operations.get(operation)
        if operation:
            return operation.run(host, instance)
        return True, {}

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

        # TODO(@tadeboro): Add support for nested property values.
        if prop in self.properties:
            return self.properties[prop].eval(self)

        # TODO(@tadeboro): Add capability access.

        # If we have no property, try searching for requirement.
        requirements = tuple(
            r for r in self.requirements if r.name == prop
        )
        if len(requirements) == 0:
            raise DataError("Cannot find property '{}'.".format(prop))
        if len(requirements) > 1:
            raise DataError("More than one requirement is named '{}'.".format(
                prop,
            ))
        return requirements[0].target.get_property(["SELF"] + rest)

    def get_attribute(self, params):
        host, prop, *rest = params

        if host != "SELF":
            raise DataError(
                "Accessing non-local stuff is bad. Fix your service template."
            )
        if host == "HOST":
            raise DataError("HOST is not yet supported in opera.")
        if len(self.instances) != 1:
            raise DataError("Cannot get an attribute from multiple instances")

        return next(iter(self.instances.values())).get_attribute(params)

    def get_input(self, params):
        return self.topology.get_input(params)
