from .notification_definition import NotificationDefinition
from .operation_definition_for_type import OperationDefinitionForType
from .parameter_definition import ParameterDefinition
from ..entity import TypeEntity
from ..map import Map
from ..reference import Reference


class InterfaceType(TypeEntity):
    REFERENCE = Reference("interface_types")
    ATTRS = dict(
        inputs=Map(ParameterDefinition),
        operations=Map(OperationDefinitionForType),
        notifications=Map(NotificationDefinition),
    )
