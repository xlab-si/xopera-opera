from ..entity import Entity
from ..list import List
from ..map import Map
from ..reference import Reference, ReferenceXOR
from ..string import String
from ..void import Void

from .trigger_definition import TriggerDefinition


class PolicyDefinition(Entity):
    ATTRS = dict(
        type=Reference("policy_types"),
        description=String,
        metadata=Map(String),
        properties=Map(Void),
        targets=List(ReferenceXOR(("topology_template", "node_templates"), ("topology_template", "groups"))),
        triggers=Map(TriggerDefinition),
    )
    REQUIRED = {"type"}
