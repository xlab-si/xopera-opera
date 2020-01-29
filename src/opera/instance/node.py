from opera.error import DataError

from .base import Base


class Node(Base):
    def __init__(self, template, instance_id):
        super().__init__(template, instance_id)

        self.in_edges = {}  # This gets filled by other instances for us.
        self.out_edges = {}  # This is what we fill during the linking phase.

    def instantiate_relationships(self):
        assert self.topology, "Cannot instantiate relationships"

        for requirement in self.template.requirements:
            rname = requirement.name
            self.out_edges[rname] =  self.out_edges.get(rname, {})

            for target in requirement.target.instances.values():
                target.in_edges[rname] = target.in_edges.get(rname, {})

                rel = requirement.relationship.instantiate(self, target)
                rel.topology = self.topology
                self.out_edges[rname][target.tosca_id] = rel
                target.in_edges[rname][self.tosca_id] = rel

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

    def deploy(self):
        print("  Deploying {}".format(self.tosca_id))

        self.set_state("creating")
        self.run_operation("HOST", "Standard", "create")
        self.set_state("created")

        self.set_state("configuring")
        for requirement in self.template.requirements:
            for relationship in self.out_edges[requirement.name].values():
                relationship.run_operation(
                    "SOURCE", "Configure", "pre_configure_source",
                )
        for requirement_dependants in self.in_edges.values():
            for relationship in requirement_dependants.values():
                relationship.run_operation(
                    "TARGET", "Configure", "pre_configure_target",
                )
        self.run_operation("HOST", "Standard", "configure")
        for requirement in self.template.requirements:
            for relationship in self.out_edges[requirement.name].values():
                relationship.run_operation(
                    "SOURCE", "Configure", "post_configure_source",
                )
        for requirement_dependants in self.in_edges.values():
            for relationship in requirement_dependants.values():
                relationship.run_operation(
                    "TARGET", "Configure", "post_configure_target",
                )
        self.set_state("configured")

        self.set_state("starting")
        self.run_operation("HOST", "Standard", "start")
        self.set_state("started")

        # TODO(@tadeboro): Execute various add hooks

    def undeploy(self):
        print("  Undeploying {}".format(self.tosca_id))

        self.set_state("stopping")
        self.run_operation("HOST", "Standard", "stop")
        self.set_state("configured")

        self.set_state("deleting")
        self.run_operation("HOST", "Standard", "delete")
        self.set_state("initial")

        # TODO(@tadeboro): Execute various remove hooks

        self.reset_attributes()
        self.write()

    #
    # TOSCA functions
    #
    def get_attribute(self, params):
        host, attr, *rest = params

        if host != "SELF":
            raise DataError(
                "Accessing non-local stuff is bad. Fix your service template."
            )
        if host == "HOST":
            raise DataError("HOST is not yet supported in opera.")

        # TODO(@tadeboro): Add support for nested attribute values once we
        # have data type support.
        if attr in self.attributes:
            return self.attributes[attr].eval(self)

        # TODO(@tadeboro): Add capability access.

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
