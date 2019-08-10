from ..entity import Entity
from ..list import List
from ..reference import Reference
from ..string import String

from .constraint_clause import ConstraintClause


class SchemaDefinition(Entity):
    ATTRS = dict(
        type=Reference("data_types"),
        description=String,
        constraints=List(ConstraintClause),
    )
    REQUIRED = {"type"}
