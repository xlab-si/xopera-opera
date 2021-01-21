from .activity_definition import ActivityDefinition
from .condition_clause_definition import ConditionClauseDefinition
from .event_filter_definition import EventFilterDefinition
from .time_interval import TimeInterval
from ..entity import Entity
from ..integer import Integer
from ..list import List
from ..string import String
from ..type import Type
from ..void import Void


class TriggerDefinition(Entity):
    ATTRS = dict(
        description=String,
        event=String,
        schedule=TimeInterval,
        target_filter=EventFilterDefinition,
        condition=List(ConditionClauseDefinition),
        action=List(ActivityDefinition),
    )
    REQUIRED = {"event", "action"}

    @classmethod
    def validate(cls, yaml_node):
        if "condition" in yaml_node.bare:
            condition = yaml_node.bare["condition"]
            if isinstance(condition, list):
                pass
            elif isinstance(condition, dict):
                cls.ATTRS["condition"] = TriggerExtendedConditionNotation
            else:
                cls.abort("Bad policy condition definition.", yaml_node.loc)
        super().validate(yaml_node)


class TriggerExtendedConditionNotation(Entity):
    ATTRS = dict(
        constraint=List(ConditionClauseDefinition),
        period=Void,
        evaluations=Integer,
        method=String,
    )

    @classmethod
    def validate(cls, yaml_node):
        if "period" in yaml_node.bare:
            cls.ATTRS["period"] = Type("scalar-unit.time", yaml_node.loc)
        super().validate(yaml_node)
