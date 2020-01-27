from opera.template.topology import Topology

from ..entity import Entity
from ..map import Map
from ..string import String

from .group_definition import GroupDefinition
from .node_template import NodeTemplate
from .parameter_definition import ParameterDefinition
from .policy_definition import PolicyDefinition
from .relationship_template import RelationshipTemplate


class TopologyTemplate(Entity):
    ATTRS = dict(
        description=String,
        inputs=Map(ParameterDefinition),
        node_templates=Map(NodeTemplate),
        relationship_templates=Map(RelationshipTemplate),
        groups=Map(GroupDefinition),
        policies=Map(PolicyDefinition),
        outputs=Map(ParameterDefinition),
        # TODO(@tadeboro): substitution_mappings and workflows
    )

    def get_template(self, service_ast):
        topology = Topology(
            nodes={
                name: node_ast.get_template(name, service_ast)
                for name, node_ast in self.node_templates.items()
            },
        )
        topology.resolve_requirements()
        return topology
