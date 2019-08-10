from ..entity import Entity
from ..void import Void


class ConstraintClause(Entity):
    ATTRS = dict(
        equal=Void,
        greater_than=Void,
        greater_or_equal=Void,
        less_than=Void,
        less_or_equal=Void,
        in_range=Void,
        valid_values=Void,
        length=Void,
        min_length=Void,
        max_length=Void,
        pattern=Void,
        schema=Void,
    )

    @classmethod
    def validate(cls, yaml_node):
        super().validate(yaml_node)
        if len(yaml_node.value) != 1:
            cls.abort("Expected single-pair map.", yaml_node.loc)
