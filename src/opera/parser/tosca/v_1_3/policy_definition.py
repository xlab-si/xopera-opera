from ..entity import Entity
from ..map import Map
from ..reference import Reference
from ..string import String
from ..void import Void


class PolicyDefinition(Entity):
    ATTRS = dict(
        type=Reference("policy_types"),
        description=String,
        metadata=Map(String),
        properties=Map(Void),
        # TODO(@tadeboro): targets, triggers
    )
    REQUIRED = {"type"}
