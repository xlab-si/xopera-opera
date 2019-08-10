from ..entity import TypeEntity
from ..map import Map
from ..reference import Reference
from ..string import String

from .notification_definition import NotificationDefinition
from .operation_definition_for_type import OperationDefinitionForType
from .property_definition import PropertyDefinition


class InterfaceType(TypeEntity):
    REFERENCE = Reference("interface_types")
    ATTRS = dict(
        inputs=Map(PropertyDefinition),
        operations=Map(OperationDefinitionForType),
        notifications=Map(NotificationDefinition),
    )
