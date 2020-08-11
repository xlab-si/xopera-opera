from collections import Counter

from opera.error import DataError
from opera.instance.node import Node as Instance
from pathlib import Path


class Node:
    def __init__(
            self,
            name,
            types,
            properties,
            attributes,
            requirements,
            capabilities,
            interfaces,
            artifacts,
    ):
        self.name = name
        self.types = types
        self.properties = properties
        self.attributes = attributes
        self.requirements = requirements
        self.capabilities = capabilities
        self.interfaces = interfaces
        self.artifacts = artifacts

        # This will be set when the node is inserted into a topology
        self.topology = None

        # This will be set at instantiation time.
        self.instances = None

    def resolve_requirements(self, topology):
        requirement_occurrences = Counter([r.name for r in self.requirements])
        for r in self.requirements:
            occurrences_range = r.occurrences.data if r.occurrences else None
            min_occurrences = occurrences_range[0] if occurrences_range else 1
            max_occurrences = occurrences_range[1] if occurrences_range else 1

            if requirement_occurrences[r.name] < min_occurrences:
                raise DataError(
                    "Not enough occurrences found for requirement '{}'. "
                    "Minimum is: {}".format(
                        r.name, min_occurrences
                    ))
            if requirement_occurrences[r.name] > max_occurrences:
                raise DataError(
                    "Too many occurrences found for requirement '{}'. "
                    "Maximum is: {}".format(
                        r.name, max_occurrences
                    ))
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
            return instance.attributes["public_address"].eval(
                self, "public_address"
            )

        host = next((
            r.target.get_host()
            for r in self.requirements
            if r.relationship.is_a("tosca.relationships.HostedOn")
        ), None)

        return host or "localhost"

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

        # TODO(@tadeboro): Add support for nested property values.
        if prop in self.properties:
            return self.properties[prop].eval(self, prop)

        # Check if there are capability and requirement with the same name.
        if prop in [r.name for r in self.requirements] and prop \
                in [c.name for c in self.capabilities]:
            raise DataError("There are capability and requirement with the "
                            "same name: '{}'.".format(prop, ))

        # If we have no property, try searching for capability.
        capabilities = tuple(
            c for c in self.capabilities if c.name == prop
        )
        if len(capabilities) > 1:
            raise DataError("More than one capability is named '{}'.".format(
                prop,
            ))

        if len(capabilities) == 1 and capabilities[0].properties:
            return capabilities[0].properties[0].get(rest[0]).data

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
        host, attr, *rest = params

        if host == "HOST":
            raise DataError("HOST is not yet supported in opera.")
        if host != "SELF":
            raise DataError(
                "Attribute host should be set to 'SELF' which is the only "
                "valid value. This is needed to indicate that the attribute "
                "is referenced locally from something in the node itself."
            )
        if len(self.instances) != 1:
            raise DataError("Cannot get an attribute from multiple instances")

        return next(iter(self.instances.values())).get_attribute(params)

    def get_input(self, params):
        return self.topology.get_input(params)

    def map_attribute(self, params, value):
        host, prop, *rest = params

        if host == "HOST":
            raise DataError("HOST is not yet supported in opera.")
        if host != "SELF":
            raise DataError(
                "Attribute host should be set to 'SELF' which is the only "
                "valid value. This is needed to indicate that the attribute "
                "is referenced locally from something in the node itself."
            )

        if len(self.instances) != 1:
            raise DataError(
                "Mapping an attribute for multiple instances not supported")

        next(iter(self.instances.values())).map_attribute(params, value)

    def get_artifact(self, params):
        host, prop, *rest = params

        location = None
        remove = None

        if len(rest) == 1:
            location = rest[0]

        if len(rest) == 2:
            location, remove = rest

        if host == "HOST":
            raise DataError("HOST is not yet supported in opera.")
        if host != "SELF":
            raise DataError(
                "Artifact host should be set to 'SELF' which is the only "
                "valid value. This is needed to indicate that the artifact "
                "is referenced locally from something in the node itself."
            )

        if location == "LOCAL_FILE":
            raise DataError("Location get_artifact property is "
                            "not yet supported in opera.")

        if remove:
            raise DataError("Remove get_artifact property artifacts is "
                            "not yet supported in opera.")

        if prop in self.artifacts:
            self.artifacts[prop].eval(self, prop)
            return Path(self.artifacts[prop].data).name
        else:
            raise DataError("Cannot find artifact '{}'.".format(prop))

    def concat(self, params):
        return self.topology.concat(params, self)

    def join(self, params):
        return self.topology.join(params, self)

    def token(self, params):
        return self.topology.token(params)
