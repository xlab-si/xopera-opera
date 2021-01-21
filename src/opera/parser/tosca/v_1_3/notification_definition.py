from .notification_implementation_definition import (
    NotificationImplementationDefinition,
)
from ..entity import Entity
from ..list import List
from ..map import Map
from ..string import String
from ..void import Void


class NotificationDefinition(Entity):
    ATTRS = dict(
        description=String,
        implementation=NotificationImplementationDefinition,
        outputs=Map(List(Void)),
    )
