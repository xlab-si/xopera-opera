from opera.error import DataError
from .base import Base
from opera.threading import utils as thread_utils


class Node(Base):
    def __init__(self, template, instance_id):
        super().__init__(template, instance_id)

        self.in_edges = {}  # This gets filled by other instances for us.
        self.out_edges = {}  # This is what we fill during the linking phase.

    def instantiate_relationships(self):
        assert self.topology, "Cannot instantiate relationships"

        for requirement in self.template.requirements:
            rname = requirement.name
            self.out_edges[rname] = self.out_edges.get(rname, {})

            for target in requirement.target.instances.values():
                target.in_edges[rname] = target.in_edges.get(rname, {})

                rel_instances = requirement.relationship.instantiate(self, target)
                for rel in rel_instances:
                    rel.topology = self.topology
                    self.out_edges[rname][target.tosca_id] = rel
                    target.in_edges[rname][self.tosca_id] = rel
                    target.in_edges[rname][self.tosca_id] = rel
                    rel.read()

    @property
    def deployed(self):
        return self.state == "started"

    @property
    def undeployed(self):
        return self.state == "initial"

    @property
    def ready_for_deploy(self):
        return all(
            relationship.target.deployed
            for requirement_relationships in self.out_edges.values()
            for relationship in requirement_relationships.values()
        )

    @property
    def ready_for_undeploy(self):
        return all(
            relationship.source.undeployed
            for requirement_relationships in self.in_edges.values()
            for relationship in requirement_relationships.values()
        )

    def get_host(self):
        # Try to transitively find a HostedOn requirement and resort to
        # localhost if nothing suitable is found.
        return self.template.get_host() or "localhost"

    def deploy(self, verbose, workdir):
        thread_utils.print_thread("  Deploying {}".format(self.tosca_id))

        self.set_state("creating")
        self.run_operation("HOST", "Standard", "create", verbose, workdir)
        self.set_state("created")

        self.set_state("configuring")
        for requirement in set([r.name for r in self.template.requirements]):
            for relationship in self.out_edges[requirement].values():
                relationship.run_operation(
                    "SOURCE", "Configure", "pre_configure_source", verbose,
                    workdir
                )
        for requirement_dependants in self.in_edges.values():
            for relationship in requirement_dependants.values():
                relationship.run_operation(
                    "TARGET", "Configure", "pre_configure_target", verbose,
                    workdir
                )
        self.run_operation("HOST", "Standard", "configure", verbose, workdir)
        for requirement in set([r.name for r in self.template.requirements]):
            for relationship in self.out_edges[requirement].values():
                relationship.run_operation(
                    "SOURCE", "Configure", "post_configure_source", verbose,
                    workdir
                )
        for requirement_dependants in self.in_edges.values():
            for relationship in requirement_dependants.values():
                relationship.run_operation(
                    "TARGET", "Configure", "post_configure_target", verbose,
                    workdir
                )
        self.set_state("configured")

        self.set_state("starting")
        self.run_operation("HOST", "Standard", "start", verbose, workdir)
        self.set_state("started")

        # TODO(@tadeboro): Execute various add hooks
        thread_utils.print_thread(
            "  Deployment of {} complete".format(self.tosca_id)
        )

    def undeploy(self, verbose, workdir):
        thread_utils.print_thread("  Undeploying {}".format(self.tosca_id))

        self.set_state("stopping")
        self.run_operation("HOST", "Standard", "stop", verbose, workdir)
        self.set_state("configured")

        self.set_state("deleting")
        self.run_operation("HOST", "Standard", "delete", verbose, workdir)
        self.set_state("initial")

        # TODO(@tadeboro): Execute various remove hooks

        self.reset_attributes()
        self.write()

        thread_utils.print_thread(
            "  Undeployment of {} complete".format(self.tosca_id)
        )

    #
    # TOSCA functions
    #
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

        # TODO(@tadeboro): Add support for nested attribute values once we
        # have data type support.
        if attr in self.attributes:
            return self.attributes[attr].eval(self, attr)

        # Check if there are capability and requirement with the same name.
        if attr in self.out_edges and attr in [c.name for c in
                                               self.template.capabilities]:
            raise DataError("There are capability and requirement with the "
                            "same name: '{}'.".format(attr, ))

        # If we have no attribute, try searching for capability.
        capabilities = tuple(
            c for c in self.template.capabilities if c.name == attr
        )
        if len(capabilities) > 1:
            raise DataError(
                "More than one capability is named '{}'.".format(attr, ))

        if len(capabilities) == 1 and capabilities[0].attributes and len(
                rest) != 0:
            return capabilities[0].attributes.get(rest[0]).data

        # If we have no attribute, try searching for requirement.
        relationships = self.out_edges.get(attr, {})
        if len(relationships) == 0:
            raise DataError("Cannot find attribute '{}'.".format(attr))
        if len(relationships) > 1:
            raise DataError(
                "Targeting more than one instance via '{}'.".format(attr),
            )
        return next(iter(relationships.values())).target.get_attribute(
            ["SELF"] + rest,
        )

    def get_property(self, params):
        return self.template.get_property(params)

    def get_input(self, params):
        return self.template.get_input(params)

    def map_attribute(self, params, value):
        host, attr, *rest = params

        if host == "HOST":
            raise DataError("HOST is not yet supported in opera.")
        if host != "SELF":
            raise DataError(
                "Attribute host should be set to 'SELF' which is the only "
                "valid value. This is needed to indicate that the attribute "
                "is referenced locally from something in the node itself."
            )

        # TODO(@tadeboro): Add support for nested attribute values once we
        # have data type support.
        if attr not in self.attributes:
            raise DataError("Cannot find attribute '{}'.".format(attr))

        self.set_attribute(attr, value)

    def get_artifact(self, params):
        return self.template.get_artifact(params)

    def concat(self, params):
        return self.template.concat(params)

    def join(self, params):
        return self.template.join(params)

    def token(self, params):
        return self.template.token(params)
