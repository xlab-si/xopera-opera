from ..entity import Entity
from ..string import String
from ..list import List
from ..map import Map
from ..void import Void

from .notification_implementation_definition import (
    NotificationImplementationDefinition,
)


class NotificationDefinition(Entity):
    ATTRS = dict(
        description=String,
        implementation=NotificationImplementationDefinition,
        outputs=Map(List(Void)),
    )
