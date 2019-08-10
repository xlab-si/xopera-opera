from ..entity import Entity
from ..list import List
from ..void import Void


# NOTE: This is more or less unimplemented, since we do not intend to support
# node filtering. Official grammar for filters being a complete garbage only
# makes our decision of not supporting them easier to defend.


class NodeFilterDefinition(Entity):
    ATTRS = dict(
        properties=List(Void),
        capabilities=List(Void),
    )
