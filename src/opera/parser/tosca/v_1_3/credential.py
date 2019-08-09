from ..entity import Entity
from ..map import Map
from ..string import String


class Credential(Entity):
    ATTRS = dict(
        protocol=String,
        token_type=String,
        token=String,
        keys=Map(String),
        user=String,
    )
    REQUIRED = {"token"}
