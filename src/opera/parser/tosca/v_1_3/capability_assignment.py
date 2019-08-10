from ..entity import Entity
from ..map import Map
from ..string import String
from ..void import Void

from .range import Range


class CapabilityAssignment(Entity):
    ATTRS = dict(
        properties=Map(Void),
        attributes=Map(Void),
        occurrences=Range,
    )
