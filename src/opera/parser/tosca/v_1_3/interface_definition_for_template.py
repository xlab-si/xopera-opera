from .notification_definition import NotificationDefinition
from .operation_definition_for_template import OperationDefinitionForTemplate
from ..entity import Entity
from ..map import Map
from ..void import Void


class InterfaceDefinitionForTemplate(Entity):
    ATTRS = dict(
        inputs=Map(Void),
        operations=Map(OperationDefinitionForTemplate),
        notifications=Map(NotificationDefinition),
    )
