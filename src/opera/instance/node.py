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
