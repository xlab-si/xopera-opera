from ..entity import Entity
from ..timestamp import Timestamp


class TimeInterval(Entity):
    ATTRS = dict(
        start_time=Timestamp,
        end_time=Timestamp,
    )
    REQUIRED = {"start_time", "end_time"}
