from ..entity import Entity
from ..reference import Reference
from ..string import String
from ..void import Void

from .schema_definition import SchemaDefinition
from .status import Status


class AttributeDefinition(Entity):
    ATTRS = dict(
        type=Reference("data_types"),
        description=String,
        default=Void,
        status=Status,
        key_schema=SchemaDefinition,
        entry_schema=SchemaDefinition,
    )
    REQUIRED = {"type"}
