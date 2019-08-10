from ..entity import Entity
from ..map import Map
from ..string import String
from ..void import Void

from .notification_definition import NotificationDefinition
from .operation_definition_for_template import OperationDefinitionForTemplate


class InterfaceDefinitionForTemplate(Entity):
    ATTRS = dict(
        inputs=Map(Void),
        operations=Map(OperationDefinitionForTemplate),
        notifications=Map(NotificationDefinition),
    )
