from .range import Range
from ..entity import Entity
from ..map import Map
from ..void import Void


class CapabilityAssignment(Entity):
    ATTRS = dict(
        properties=Map(Void),
        attributes=Map(Void),
        occurrences=Range
    )
