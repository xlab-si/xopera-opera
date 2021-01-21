from typing import Dict, Union, Type

from .parameter_definition import ParameterDefinition
from ..base import Base
from ..entity import Entity
from ..list import List
from ..map import Map
from ..reference import Reference, ReferenceXOR
from ..string import String
from ..void import Void

T_ATTR = Dict[str, Union[Type[Base], Base, Map, List, Reference, ReferenceXOR]]


class ActivityDefinition(Entity):
    ATTRS: T_ATTR = dict()

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
    ATTRS: T_ATTR = dict(
        delegate=Void,
        workflow=String,
        inputs=Map(ParameterDefinition),
    )
    REQUIRED = {"delegate"}


class SetStateActivityDefinition(Entity):
    ATTRS: T_ATTR = dict(
        set_state=Void,
    )
    REQUIRED = {"set_state"}


class CallOperationActivityDefinition(Entity):
    ATTRS: T_ATTR = dict(
        call_operation=Void,
        operation=String,
        inputs=Map(ParameterDefinition),
    )
    REQUIRED = {"call_operation"}


class InlineWorkflowActivityDefinition(Entity):
    ATTRS: T_ATTR = dict(
        inline=Void,
        workflow=String,
        inputs=Map(ParameterDefinition),
    )
    REQUIRED = {"inline"}
