from ..entity import TypeEntity
from ..list import List
from ..map import Map
from ..reference import Reference
from ..string import String

from .property_definition import PropertyDefinition


class ArtifactType(TypeEntity):
    REFERENCE = Reference("artifact_types")
    ATTRS = dict(
        mime_type=String,
        file_ext=List(String),
        properties=Map(PropertyDefinition),
    )
