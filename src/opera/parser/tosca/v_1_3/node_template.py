from ..entity import Entity
from ..list import List
from ..map import Map, OrderedMap
from ..reference import Reference
from ..string import String
from ..void import Void

from .artifact_definition import ArtifactDefinition
from .capability_assignment import CapabilityAssignment
from .interface_definition_for_template import InterfaceDefinitionForTemplate
from .node_filter_definition import NodeFilterDefinition
from .requirement_assignment import RequirementAssignment


# NOTE: We deviate form the TOSCA standard in attribute assignment statement,
# since the official grammar is just ridiculous (it makes assigning complex
# values impossible in simplified form).


class NodeTemplate(Entity):
    ATTRS = dict(
        type=Reference("node_types"),
        description=String,
        metadata=Map(String),
        directives=List(String),
        properties=Map(Void),
        attributes=Map(Void),
        requirements=OrderedMap(RequirementAssignment),
        capabilities=Map(CapabilityAssignment),
        interfaces=Map(InterfaceDefinitionForTemplate),
        artifacts=Map(ArtifactDefinition),
        node_filter=NodeFilterDefinition,
        copy=Reference("topology_template", "node_templates"),
    )
    REQUIRED = {"type"}
