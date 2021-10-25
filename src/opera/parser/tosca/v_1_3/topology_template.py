from opera.error import DataError
from opera.template.topology import Topology
from .group_definition import GroupDefinition
from .node_template import NodeTemplate
from .parameter_definition import ParameterDefinition
from .policy_definition import PolicyDefinition
from .relationship_template import RelationshipTemplate
from ..entity import Entity
from ..list import List
from ..map import Map
from ..string import String


class TopologyTemplate(Entity):
    ATTRS = dict(
        description=String,
        inputs=Map(ParameterDefinition),
        node_templates=Map(NodeTemplate),
        relationship_templates=Map(RelationshipTemplate),
        groups=Map(GroupDefinition),
        policies=List(Map(PolicyDefinition)),
        outputs=Map(ParameterDefinition),
        # TODO(@tadeboro): substitution_mappings and workflows
    )

    def get_template(self, inputs, service_ast):
        # nodes will be used also for collecting policies so retrieve them here only once
        nodes = {name: node_ast.get_template(name, service_ast)
                 for name, node_ast in self.get("node_templates", {}).items()}

        topology = Topology(
            inputs=self.collect_inputs(inputs, service_ast),
            outputs=self.collect_outputs(service_ast),
            nodes=nodes,
            relationships={
                name: rel_ast.get_template(name, service_ast)
                for name, rel_ast in self.get("relationship_templates", {}).items()
            },
            policies=[
                next(pol_ast.get_template(name, service_ast, nodes) for name, pol_ast in pol.items())
                for pol in self.get("policies", [])
            ]
        )
        topology.resolve_requirements()
        topology.resolve_policies()
        return topology

    def collect_inputs(self, inputs, service_ast):
        declared_inputs = self.get("inputs", {})
        undeclared_inputs = set(inputs.keys()) - declared_inputs.keys()

        if undeclared_inputs:
            raise DataError(f"Undeclared inputs: {', '.join(undeclared_inputs)}")

        input_values = {
            name: definition.get_value(definition.get_value_type(service_ast))
            for name, definition in declared_inputs.items()
        }

        for name, value in inputs.items():
            input_values[name].set(value)

        return input_values

    def collect_outputs(self, service_ast):
        return {
            name: dict(
                description=getattr(definition.get("description"), "data", ""),
                value=definition.get_value(definition.get_value_type(service_ast)),
            ) for name, definition in self.get("outputs", {}).items()
        }

    def merge(self, other):
        for key in (
                "inputs",
                "node_templates",
                "data_types",
                "relationship_templates",
                "groups",
                "policies",
                "outputs"
        ):
            if key not in other.data:
                continue
            if key in self.data:
                self.data[key].merge(other.data[key])
            else:
                self.data[key] = other.data[key]
