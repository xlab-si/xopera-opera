from .parameter_definition import ParameterDefinition
from ..entity import Entity
from ..map import Map
from ..string import String
from ..void import Void


class ActivityDefinition(Entity):
    ATTRS = dict()

    @classmethod
    def validate(cls, yaml_node):
        for key in yaml_node.bare:
            if key == "delegate":
                cls.ATTRS = DelegateWorkflowActivityDefinition.ATTRS
            elif key == "set_state":
                cls.ATTRS = SetStateActivityDefinition.ATTRS
            elif key == "call_operation":
                cls.ATTRS = CallOperationActivityDefinition.ATTRS
            elif key == "inline":
                cls.ATTRS = InlineWorkflowActivityDefinition.ATTRS
            else:
                cls.abort("Bad activity definition.", yaml_node.loc)
        super().validate(yaml_node)


class DelegateWorkflowActivityDefinition(Entity):
    ATTRS = dict(
        delegate=Void,
        workflow=String,
        inputs=Map(ParameterDefinition),
    )
    REQUIRED = {"delegate"}


class SetStateActivityDefinition(Entity):
    ATTRS = dict(
        set_state=Void,
    )
    REQUIRED = {"set_state"}


class CallOperationActivityDefinition(Entity):
    ATTRS = dict(
        call_operation=Void,
        operation=String,
        inputs=Map(ParameterDefinition),
    )
    REQUIRED = {"call_operation"}


class InlineWorkflowActivityDefinition(Entity):
    ATTRS = dict(
        inline=Void,
        workflow=String,
        inputs=Map(ParameterDefinition),
    )
    REQUIRED = {"inline"}
