import collections
import json

from opera import operations


class Instance(object):
    def __init__(self, name, template):
        self.template = template
        self.attributes = dict(
            tosca_name=name,
            tosca_id=name + ".0",  # TODO/@tadeboro): add id generator
            state="initial",  # TODO(@tadeboro): replace with enum
        )

        # Graph fields
        self.requirements = {}

    @property
    def id(self):
        return self.attributes["tosca_id"]

    @property
    def name(self):
        return self.attributes["tosca_name"]

    @property
    def path(self):
        return "{}.data".format(self.id)

    def save(self):
        with open(self.path, "w") as fd:
            json.dump(self.attributes, fd, indent=2, separators=(',', ': '))

    def load(self):
        with open(self.path, "r") as fd:
            self.attributes = json.load(fd)

    def get_operation(self, interface, name):
        implementation, inputs = self.template.get_operation(interface, name)
        return operations.Operation(self, implementation, inputs)

    def set_state(self, state):
        self.attributes["state"] = state
        self.save()

    def execute_workflow(self, workflow):
        for step, (transition_state, end_state) in workflow.items():
            self.set_state(transition_state)
            operation = self.get_operation("Standard", step)
            success, attributes = operation.run()
            # TODO(@tadeboro): Handle failure here
            self.attributes.update(attributes)
            self.set_state(end_state)

    def deploy(self):
        print("  Processing {} ...".format(self.id))
        self.execute_workflow(dict(
            create=("creating", "created"),
            configure=("configuring", "configured"),
            start=("starting", "started"),
        ))

    def undeploy(self):
        self.execute_workflow(dict(
            stop=("stopping", "configured"),
            delete=("deleting", "initial"),
        ))

    def get_property(self, *path):
        return self.template.get_property(*path)

    def get_attribute(self, path):
        if path[0] not in ("SELF", "SOURCE", "TARGET"):
            raise Exception(
                "Accessing non-local stuff bad. Fix your service template."
            )
        return None


class InstanceModel(object):
    def __init__(self, service_template):
        self.service_template = service_template
        self.nodes = {}
        self.edges = collections.defaultdict(set)
        self.name_ids_lut = collections.defaultdict(set)

    def add(self, instances):
        for i in instances:
            self.nodes[i.id] = i
            self.name_ids_lut[i.name].add(i.id)

    def link(self):
        for id, instance in self.nodes.items():
            reqs = instance.template.dig("requirements")
            if reqs:
                for kind, node in reqs.items():
                    instance.requirements[kind] = {
                        self.nodes[i] for i in self.name_ids_lut[node.name]
                    }
                    self.edges[id].update(self.name_ids_lut[node.name])

    def deploy(self):
        for id in self.ordered_instance_ids:
            self.nodes[id].deploy()

    def undeploy(self):
        for id in reversed(self.ordered_instance_ids):
            self.nodes[id].undeploy()

    @property
    def ordered_instance_ids(self):
        # Marks: 0 - unmarked, 1 - temporary, 2 - permanently
        marks = collections.defaultdict(lambda: 0)
        ordered_ids = []

        def visit(id):
            if marks[id] == 2:
                return
            if marks[id] == 1:
                raise Exception("Template has a cycle")
            marks[id] = 1
            for requirement in self.edges[id]:
                visit(requirement)
            marks[id] = 2
            ordered_ids.append(id)

        for id in self.nodes:
            if marks[id] == 0:
                visit(id)
        return ordered_ids

    def __str__(self):
        return "\n".join("{} -> {}".format(*i) for i in self.edges.items())
