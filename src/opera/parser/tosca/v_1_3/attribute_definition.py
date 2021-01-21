from opera.value import Value
from .schema_definition import SchemaDefinition
from .status import Status
from ..entity import Entity
from ..reference import DataTypeReference
from ..string import String
from ..void import Void


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

    def get_value_type(self, service_ast):  # pylint: disable=no-self-use
        # TODO(@tadeboro): Implement type checks later.
        return None
