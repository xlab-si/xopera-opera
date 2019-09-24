import collections
import json
from typing import Dict, Tuple, Optional, DefaultDict, List

from opera import operations
from opera.log import get_logger
from opera.operations import Operation
from opera.parser.tosca.v_1_3 import ServiceTemplate


logger = get_logger()


class Instance:
    def __init__(self, name: str, template):
        self.template = template
        self.attributes: Dict[str, str] = dict(
            tosca_name=name,
            tosca_id=name + ".0",  # TODO/@tadeboro): add id generator
            state="initial",  # TODO(@tadeboro): replace with enum
        )

        # Graph fields
        self.requirements: Dict[str, List["Instance"]] = {}

    # pylint: disable=invalid-name
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

    def get_operation(self, interface: str, name: str) -> Operation:
        implementation, inputs = self.template.get_operation(interface, name)
        return operations.Operation(self, implementation, inputs)

    def set_state(self, state):
        self.attributes["state"] = state
        self.save()

    def execute_workflow(self, workflow: Dict[str, Tuple[str, str]]):
        for step, (transition_state, end_state) in workflow.items():
            self.set_state(transition_state)
            operation = self.get_operation("Standard", step)
            success, attributes = operation.run()  # pylint: disable=unused-variable
            # TODO(@tadeboro): Handle failure here
            self.attributes.update(attributes)
            self.set_state(end_state)

    def deploy(self):
        logger.info("  Processing %s ...", self.id)
        self.execute_workflow(dict(
            create=("creating", "created"),
            configure=("configuring", "configured"),
            start=("starting", "started"),
        ))

    def undeploy(self):
        logger.info("  Processing %s ...", self.id)
        self.execute_workflow(dict(
            stop=("stopping", "configured"),
            delete=("deleting", "initial"),
        ))

    def get_property(self, *path):
        return self.template.get_property(*path)

    def get_requirement_attribute(self, name: str, *path: str) -> Optional[str]:
        if name not in self.requirements:
            return None
        if len(self.requirements[name]) != 1:
            raise Exception("Cannot get attribute from multiple instances.")
        linked_instance = next(iter(self.requirements[name]))
        return linked_instance.get_attribute("SELF", *path)

    def get_attribute(self, reference: str, name: str, *path: str) -> Optional[str]:
        if reference not in ("SELF", "SOURCE", "TARGET", "HOST"):
            raise Exception(
                "Accessing non-local stuff bad. Fix your service template."
            )

        # TODO(@tadeboro): Add support for nested attribute values once we
        # have data type support.
        if name in self.attributes:
            return self.attributes[name]

        attr = self.template.get_attribute(reference, name, *path)
        if attr:
            return attr
        return self.get_requirement_attribute(name, *path)

    def get_host(self, indirect=False) -> Optional[str]:
        if self.template.is_a("tosca.nodes.Compute"):
            if indirect:
                # TODO(@tadeboro): Think about this a bit more. Feels too
                # restrictive at the moment.
                return self.get_attribute("SELF", "public_address")
            return "localhost"

        req_name = self.template.get_hosted_on_requirement_name()
        if len(self.requirements[req_name]) != 1:
            raise Exception(
                "{} cannot be hosted on more than one node".format(self.name)
            )
        return next(iter(self.requirements[req_name])).get_host(indirect=True)


class InstanceModel:
    def __init__(self, service_template: ServiceTemplate):
        self.service_template = service_template
        self.nodes: Dict[str, Instance] = {}
        self.edges: DefaultDict[str, set] = collections.defaultdict(set)
        self.name_ids_lut: DefaultDict[str, set] = collections.defaultdict(set)

    def load(self):
        for i in self.nodes.values():
            i.load()

    def add(self, instances: List[Instance]):
        for i in instances:
            self.nodes[i.id] = i
            self.name_ids_lut[i.name].add(i.id)

    def link(self):
        for instance_id, instance in self.nodes.items():
            reqs = instance.template.dig("requirements")
            if reqs:
                for kind, node in reqs.items():
                    instance.requirements[kind] = {
                        self.nodes[i] for i in self.name_ids_lut[node.name]
                    }
                    self.edges[instance_id].update(self.name_ids_lut[node.name])

    def deploy(self):
        for instance_id in self.ordered_instance_ids:
            self.nodes[instance_id].deploy()

    def undeploy(self):
        for instance_id in reversed(self.ordered_instance_ids):
            self.nodes[instance_id].undeploy()

    @property
    def ordered_instance_ids(self) -> List[str]:
        # Marks: 0 - unmarked, 1 - temporary, 2 - permanently
        marks: DefaultDict[str, int] = collections.defaultdict(lambda: 0)
        ordered_ids = []

        def visit(instance_id):
            if marks[instance_id] == 2:
                return
            if marks[instance_id] == 1:
                raise Exception("Template has a cycle")
            marks[instance_id] = 1
            for requirement in self.edges[instance_id]:
                visit(requirement)
            marks[instance_id] = 2
            ordered_ids.append(instance_id)

        for node_id in self.nodes:
            if marks[node_id] == 0:
                visit(node_id)
        return ordered_ids

    def __str__(self):
        return "\n".join("{} -> {}".format(*i) for i in self.edges.items())
