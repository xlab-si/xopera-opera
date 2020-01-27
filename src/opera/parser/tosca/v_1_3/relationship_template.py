import collections

from opera.template.relationship import Relationship
from opera.template.operation import Operation

from ..entity import Entity
from ..map import Map
from ..reference import Reference
from ..string import String
from ..void import Void

from .collector_mixin import CollectorMixin
from .interface_definition_for_template import InterfaceDefinitionForTemplate


class RelationshipTemplate(CollectorMixin, Entity):
    ATTRS = dict(
        type=Reference("relationship_types"),
        description=String,
        metadata=Map(String),
        properties=Map(Void),
        attributes=Map(Void),
        interfaces=Map(InterfaceDefinitionForTemplate),
        copy=Reference("topology_template", "relationship_templates"),
    )
    REQUIRED = {"type"}

    def get_template(self, name, service_ast):
        return Relationship(
            name=name,
            types=self.collect_types(service_ast),
            properties=self.collect_properties(service_ast),
            attributes=self.collect_attributes(service_ast),
            interfaces=self.collect_interfaces(service_ast),
        )
