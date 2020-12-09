import pathlib

from opera.parser import yaml
from opera.parser.yaml.node import Node

from ..entity import Entity
from ..list import List
from ..map import Map
from ..string import String

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

    @classmethod
    def parse(cls, yaml_node, base_path, template_path, parsed_templates):
        service = super().parse(yaml_node)
        service.visit("prefix_path", template_path.parent)
        parsed = service.merge_imports(
            base_path, parsed_templates | set([template_path]),
        )
        return service, parsed

    def merge_imports(self, base_path, parsed_templates):
        parsed = parsed_templates.copy()

        for import_def in self.data.get("imports", []):
            import_def.file.resolve_path(base_path)
            import_path = import_def.file.data

            if import_path in parsed:
                continue

            with (base_path / import_path).open() as fd:
                yaml_data = yaml.load(fd, str(import_path))
            ast, parsed = ServiceTemplate.parse(
                yaml_data, base_path, import_path, parsed,
            )
            self.merge(ast)

        # We do not need imports anymore, since they are preprocessor
        # construct and would only clutter the AST.
        self.data.pop("imports", None)

        return parsed

    def merge(self, other):
        if self.tosca_definitions_version != other.tosca_definitions_version:
            self.abort(
                "Incompatible TOSCA definitions: {} and {}".format(
                    self.tosca_definitions_version,
                    other.tosca_definitions_version
                ), other.loc,
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

    def get_template(self, inputs):
        if "topology_template" not in self:
            self.abort("No topology template section", self.loc)

        return self.topology_template.get_template(inputs, self)
