from collections import Counter
from pathlib import Path
from typing import Dict, List, Union

from opera.constants import OperationHost, StandardInterfaceOperation, ConfigureInterfaceOperation
from opera.error import DataError
from opera.instance.base import Base
from opera.instance.node import Node as Instance
from opera.template.policy import Policy
from opera.template.topology import Topology


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

        # This will be set when the connected policies are resolved in topology.
        self.policies: List[Policy] = []

        # This will be set when the node is inserted into a topology.
        self.topology: Topology = None

        # This will be set at instantiation time.
        self.instances: Dict = None  # type: ignore

    def resolve_requirements(self, topology):
        requirement_occurrences = Counter([r.name for r in self.requirements])
        for r in self.requirements:
            occurrences_range = r.occurrences.data if r.occurrences else None
            min_occurrences = occurrences_range[0] if occurrences_range else 1
            max_occurrences = occurrences_range[1] if occurrences_range else 1

            if requirement_occurrences[r.name] < min_occurrences:
                raise DataError(
                    f"Not enough occurrences found for requirement '{r.name}'. Minimum is: {min_occurrences}"
                )
            if requirement_occurrences[r.name] > max_occurrences:
                raise DataError(f"Too many occurrences found for requirement '{r.name}'. Maximum is: {max_occurrences}")
            r.resolve(topology)

    def is_a(self, typ):
        return typ in self.types

    def instantiate(self):
        # NOTE: This is where we should handle multiple instances.
        # At the moment, we simply create one instance per node template. But
        # the algorithm is fully prepared for multiple instances.
        node_id = self.name + "_0"
        self.instances = {node_id: Instance(self, node_id)}
        return self.instances.values()

    def get_host(self):
        # TODO: Properly handle situations where multiple hosts are
        # available.

        # 1. Scan requirements for direct compute host and return one.
        # 2. Scan requirements for indirect compute host and return one.
        # 3. Default to localhost.

        host = next((
            r.target
            for r in self.requirements
            if r.relationship.is_a("tosca.relationships.HostedOn") and r.target.is_a("tosca.nodes.Compute")
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

    def run_operation(self,
                      host: OperationHost,
                      interface: str,
                      operation_type: Union[StandardInterfaceOperation, ConfigureInterfaceOperation, str],
                      instance: Base,
                      verbose: bool,
                      workdir: str,
                      validate: bool = False):
        if isinstance(operation_type, (StandardInterfaceOperation, ConfigureInterfaceOperation)):
            operation = self.interfaces[interface].operations.get(operation_type.value)
        else:
            operation = self.interfaces[interface].operations.get(operation_type)
        if operation:
            return operation.run(host, instance, verbose, workdir, validate)
        return True, {}, {}

    #
    # TOSCA functions
    #
    def get_property(self, params):
        host, prop, *rest = params

        if host == OperationHost.SELF.value:
            # TODO: Add support for nested property values.
            if prop in self.properties:
                return self.properties[prop].eval(self, prop)

            # Check if there are capability and requirement with the same name.
            if prop in [r.name for r in self.requirements] and prop in [c.name for c in self.capabilities]:
                raise DataError(f"There are capability and requirement with the same name: '{prop}'.")

            # If we have no property, try searching for capability.
            capabilities = tuple(c for c in self.capabilities if c.name == prop)
            if len(capabilities) > 1:
                raise DataError(f"More than one capability is named '{prop}'.")

            if len(capabilities) == 1 and capabilities[0].properties:
                return capabilities[0].properties.get(rest[0]).data

            # If we have no property, try searching for requirement.
            requirements = tuple(r for r in self.requirements if r.name == prop)
            if len(requirements) == 0:
                raise DataError(f"Cannot find property '{prop}'.")
            if len(requirements) > 1:
                raise DataError(f"More than one requirement is named '{prop}'.")
            return requirements[0].target.get_property([OperationHost.SELF.value] + rest)
        elif host == OperationHost.HOST.value:
            for req in self.requirements:
                # get value from the node that hosts the node as identified by its HostedOn relationship
                if "tosca.relationships.HostedOn" in req.relationship.types:
                    # TODO: Add support for nested property values.
                    if req.target and prop in req.target.properties:
                        return req.target.properties[prop].eval(self, prop)

            raise DataError(
                f"We were unable to find the property: {prop} specified with keyname: {host} for node: {self.name}. "
                f"Check if the node is connected to its host with tosca.relationships.HostedOn relationship."
            )
        elif host in (OperationHost.SOURCE.value, OperationHost.TARGET.value):
            raise DataError(f"{host} keyword can be only used within relationship template context.")
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
            # try to find the property within the connected TOSCA polices
            for policy in self.policies:
                if host == policy.name or host in policy.types:
                    # TODO: Add support for nested property values.
                    if prop in policy.properties:
                        return policy.properties[prop].eval(self, prop)

            raise DataError(
                f"We were unable to find the property: {prop} within the specified modelable entity or keyname: {host} "
                f"for node: {self.name}. The valid entities to get properties from are currently TOSCA nodes, "
                f"relationships and policies. But the best practice is that the property host is set to "
                f"'{OperationHost.SELF.value}'. This indicates that the property is referenced locally from something "
                f"in the node itself."
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

    def get_artifact(self, params):
        host, prop, *rest = params

        location = None
        remove = None

        if len(rest) == 1:
            location = rest[0]

        if len(rest) == 2:
            location, remove = rest

        if host == OperationHost.HOST.value:
            raise DataError("HOST is not yet supported in opera.")
        if host != OperationHost.SELF.value:
            raise DataError(
                f"Artifact host should be set to '{OperationHost.SELF.value}' which is the only valid value. This is "
                f"needed to indicate that the artifact is referenced locally from something in the node itself. Was: "
                f"{host}."
            )

        if location == "LOCAL_FILE":
            raise DataError("Location get_artifact property is not yet supported in opera.")

        if remove:
            raise DataError("Remove get_artifact property artifacts is not yet supported in opera.")

        if prop in self.artifacts:
            self.artifacts[prop].eval(self, prop)
            return Path(self.artifacts[prop].data).name
        else:
            raise DataError(f"Cannot find artifact '{prop}'.")

    def concat(self, params):
        return self.topology.concat(params, self)

    def join(self, params):
        return self.topology.join(params, self)

    def token(self, params):
        return self.topology.token(params)
