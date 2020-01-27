from opera.value import Value

from ..entity import Entity
from ..reference import DataTypeReference
from ..string import String
from ..void import Void

from .schema_definition import SchemaDefinition
from .status import Status


class AttributeDefinition(Entity):
    ATTRS = dict(
        type=DataTypeReference("data_types"),
        description=String,
        default=Void,
        status=Status,
        key_schema=SchemaDefinition,
        entry_schema=SchemaDefinition,
    )
    REQUIRED = {"type"}

    def get_value(self, typ):
        if "default" in self:
            return self.default.get_value(typ)
        return Value(typ, False)

    def get_value_type(self, service_ast):
        # TODO(@tadeboro): Implement type checks later.
        return None
