from ..bool import Bool
from ..entity import Entity
from ..list import List
from ..map import Map
from ..reference import DataTypeReference
from ..string import String
from ..void import Void

from .constraint_clause import ConstraintClause
from .schema_definition import SchemaDefinition
from .status import Status


class PropertyDefinition(Entity):
    ATTRS = dict(
        type=DataTypeReference("data_types"),
        description=String,
        required=Bool,
        default=Void,
        status=Status,
        constraints=List(ConstraintClause),
        key_schema=SchemaDefinition,
        entry_schema=SchemaDefinition,
        external_schema=String,
        metadata=Map(String),
    )
    REQUIRED = {"type"}
