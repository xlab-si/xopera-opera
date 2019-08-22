from ..entity import Entity
from ..list import List
from ..reference import DataTypeReference
from ..string import String

from .constraint_clause import ConstraintClause


class SchemaDefinition(Entity):
    ATTRS = dict(
        type=DataTypeReference("data_types"),
        description=String,
        constraints=List(ConstraintClause),
    )
    REQUIRED = {"type"}
