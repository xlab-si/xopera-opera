from opera.parser.yaml.node import Node
from .artifact_type import ArtifactType
from .capability_type import CapabilityType
from .data_type import DataType
from .group_type import GroupType
from .import_definition import ImportDefinition
from .interface_type import InterfaceType
from .node_type import NodeType
from .policy_type import PolicyType
from .relationship_type import RelationshipType
from .repository_definition import RepositoryDefinition
from .topology_template import TopologyTemplate
from .tosca_definitions_version import ToscaDefinitionsVersion
from ..entity import Entity
from ..list import List
from ..map import Map, MapWrapper
from ..string import String


class ServiceTemplate(Entity):
    ATTRS = dict(
        tosca_definitions_version=ToscaDefinitionsVersion,
        namespace=String,
        metadata=Map(String),
        description=String,
        # dsl_definitions have already been taken care of by the YAML parser
        repositories=Map(RepositoryDefinition),
        imports=List(ImportDefinition),
        artifact_types=Map(ArtifactType),
        data_types=Map(DataType),
        capability_types=Map(CapabilityType),
        interface_types=Map(InterfaceType),
        relationship_types=Map(RelationshipType),
        node_types=Map(NodeType),
        group_types=Map(GroupType),
        policy_types=Map(PolicyType),
        topology_template=TopologyTemplate,
    )
    REQUIRED = {"tosca_definitions_version"}

    @classmethod
    def normalize(cls, yaml_node):
        if not isinstance(yaml_node.value, dict):
            cls.abort("TOSCA document should be a map.", yaml_node.loc)

        # Filter out dsl_definitions, since they are preprocessor construct.
        return Node({
            k: v
            for k, v in yaml_node.value.items()
            if k.value != "dsl_definitions"
        }, yaml_node.loc)

    def merge(self, other: MapWrapper):
        assert isinstance(other, ServiceTemplate)

        if self.tosca_definitions_version != other.tosca_definitions_version:
            self.abort(
                "Incompatible TOSCA definitions: {} and {}".format(
                    self.tosca_definitions_version,
                    other.tosca_definitions_version
                ), other.loc
            )

        # TODO(@tadeboro): Should we merge the topology templates or should we
        # be doing substitution mapping instead?
        for key in (
                "repositories",
                "artifact_types",
                "data_types",
                "capability_types",
                "interface_types",
                "relationship_types",
                "node_types",
                "group_types",
                "policy_types",
                "topology_template",
        ):
            if key not in other.data:
                continue
            if key in self.data:
                self.data[key].merge(other.data[key])
            else:
                self.data[key] = other.data[key]

    def get_template(self):
        if "topology_template" not in self:
            self.abort("No topology template section", self.loc)
        return self.topology_template.get_template(self)
