from __future__ import print_function, unicode_literals

import collections
import sys

from opera import instances


def get_indent(n):
    return "  " * n


def format_path(path):
    return "/{}".format("/".join(path))


class MissingImplementation(Exception):
    pass


class UnknownAttribute(Exception):
    def __init__(self, path):
        super(UnknownAttribute, self).__init__(format_path(path))
        self.path = path


class BadType(Exception):
    pass


class MergeError(Exception):
    pass


class Pass(object):
    # TODO(@tadeboro): Remove when we have enough classes implemented.

    @classmethod
    def from_data(cls, data, path):
        print("Parsing {}".format(format_path(path)))
        return cls(data, path)

    def __init__(self, data, path):
        self._data = data
        self._path = path

    def __str__(self):
        return str(self._data)

    def resolve(self, _unused):
        pass


class String(object):
    @classmethod
    def from_data(cls, data, path):
        print("Parsing {}".format(format_path(path)))
        if not isinstance(data, str):
            raise BadType("String parser takes string as input data")
        return cls(data, path)

    def __init__(self, data, path):
        self._data = data
        self._path = path

    def __str__(self):
        return self._data

    def __eq__(self, other):
        return self._data == other._data

    def __ne__(self, other):
        self._data != other._data

    def resolve(self, _service_template):
        pass


class Reference(String):
    SECTION = None

    def resolve(self, service_template):
        if self.SECTION is None:
            raise MissingImplementation(
                "{} did not override SECTION".format(self.__class__.__name__)
            )

        # TODO(@tadeboro): Add target validation error messages
        self.target = service_template[self.SECTION][self._data]


class NodeTypeReference(Reference):
    SECTION = "node_types"


class Function(object):
    VALID_NAMES = (
        "concat",
        "get_artifact",
        "get_attribute",
        "get_input",
        "get_nodes_of_type",
        "get_operation_output",
        "get_property",
        "join",
        "token",
    )

    @classmethod
    def from_data(cls, data, path):
        print("Parsing {}".format(format_path(path)))
        if not isinstance(data, dict):
            raise BadType("Function constructor takes dict as input data")
        if len(data) != 1:
            raise BadType("Function constructor takes single member dict")

        (name, args), = data.items()
        if name not in cls.VALID_NAMES:
            raise BadType("Invalid function name: " + name)
        if not isinstance(args, list):
            raise BadType("Function arguments should be specified as array")

        return cls(name, args, path)

    def __init__(self, name, args, path):
        self._name = name
        self._args = args
        self._path = path

    def __str__(self):
        return "{}({})".format(self._name, ", ".join(self._args))

    def resolve(self, service_template):
        # TODO(@tadeboro): resolve arguments here
        pass


class BaseEntity(collections.OrderedDict):
    @staticmethod
    def dump_item(name, item, level):
        try:
            value = item.dump(level + 1)
            separator = "\n"
        except AttributeError:
            value = str(item)  # pass-through for native types
            separator = " "

        return "{}{}:{}{}".format(get_indent(level), name, separator, value)

    @classmethod
    def from_data(cls, data, path):
        cls.check_override()
        # TODO(@tadeboro): Add validation here
        data = cls.normalize_data(data)
        if not isinstance(data, dict):
            raise BadType("Entity constructor takes dict as input data")
        instance = cls(cls.parse(data, path))
        instance._path = path
        return instance

    @classmethod
    def parse(cls, data, path):
        print("Parsing {}".format(format_path(path)))
        return {k: cls.parse_attr(k, v, path + [k]) for k, v in data.items()}

    @classmethod
    def normalize_data(cls, data):
        # By default, no normalization is needed
        return data

    def __str__(self):
        return self.dump(0)

    def dump(self, level):
        return "\n".join(self.dump_item(k, v, level) for k, v in self.items())


class Entity(BaseEntity):
    ATTRS = None  # This should be overridden in derived classes

    @classmethod
    def check_override(cls):
        if cls.ATTRS is None:
            raise MissingImplementation(
                "{} did not override ATTRS".format(cls.__name__)
            )

    @classmethod
    def parse_attr(cls, name, data, path):
        classes = cls.ATTRS.get(name)
        if classes is None:
            raise UnknownAttribute(path)

        for c in classes:
            try:
                return c.from_data(data, path)
            except BadType:
                pass

        raise BadType("Cannot parse {}".format(format_path(path)))

    def resolve(self, service_template):
        for k in self:
            self[k].resolve(service_template)


class EntityCollection(Entity):
    ITEM_CLASS = None  # This should be overridden in derived classes

    @classmethod
    def check_override(cls):
        super(EntityCollection, cls).check_override()
        if cls.ITEM_CLASS is None:
            raise MissingImplementation(
                "{} did not override ITEM_CLASS".format(cls.__name__)
            )

    @classmethod
    def parse_attr(cls, name, data, path):
        try:
            return super(EntityCollection, cls).parse_attr(name, data, path)
        except UnknownAttribute:
            return cls.ITEM_CLASS.from_data(data, path)


class OrderedEntityCollection(EntityCollection):
    ATTRS = {}  # Ordered collections have no extra fields

    @classmethod
    def normalize_data(cls, data):
        # Convert list of single-entry dicts into ordered dict
        result = collections.OrderedDict()
        for item in data:
            (k, v), = item.items()
            result[k] = v
        return result


class Interface(Entity):
    ATTRS = dict(
        inputs=(Pass,),
        create=(Pass,),
        delete=(Pass,),
    )


class InterfaceCollection(EntityCollection):
    ATTRS = {}
    ITEM_CLASS = Interface


class NodeTemplate(Entity):
    ATTRS = dict(
        interfaces=(InterfaceCollection,),
        type=(NodeTypeReference,),

        properties=(Pass,),
        requirements=(Pass,),
    )

    def instantiate(self, name, inputs):
        instance = instances.NodeInstance.from_template(name, self, inputs)
        instance.save()  # TODO(@tadeboro): path for persisting
        return instance


class NodeTemplateCollection(EntityCollection):
    ATTRS = {}
    ITEM_CLASS = NodeTemplate


class TopologyTemplate(Entity):
    ATTRS = dict(
        node_templates=(NodeTemplateCollection,),
    )


class ArtifactDefinition(Entity):
    pass


class ArtifactDefinitionCollection(EntityCollection):
    ATTRS = {}
    ITEM_CLASS = ArtifactDefinition


class AttributeDefinition(Entity):
    ATTRS = dict(
        description=(String,),

        default=(Pass,),
        type=(String,),
        entry_schema=(Pass,),
    )


class AttributeDefinitionCollection(EntityCollection):
    ATTRS = {}
    ITEM_CLASS = AttributeDefinition


class CapabilityDefinition(Entity):
    ATTRS = dict(
        type=(String,),
        valid_source_types=(Pass,),
    )


class CapabilityDefinitionCollection(EntityCollection):
    ATTRS = {}
    ITEM_CLASS = CapabilityDefinition


class OperationImplementationDefinition(Entity):
    ATTRS = dict(
        primary=(String,),
    )


class ParameterDefinition(Entity):
    ATTRS = dict(
        default=(Function, String),
    )


class ParameterDefinitionCollection(EntityCollection):
    ATTRS = {}
    ITEM_CLASS = ParameterDefinition


class OperationDefinition(Entity):
    ATTRS = dict(
        inputs=(ParameterDefinitionCollection,),
        implementation=(OperationImplementationDefinition, String),
    )


class InterfaceDefinition(EntityCollection):
    ATTRS = dict(
        type=(Pass,),
    )
    ITEM_CLASS = OperationDefinition


class InterfaceDefinitionCollection(EntityCollection):
    ATTRS = {}
    ITEM_CLASS = InterfaceDefinition


class PropertyDefinition(Entity):
    ATTRS = dict(
        default=(Pass,),
        description=(Pass,),
        type=(Pass,),
    )


class PropertyDefinitionCollection(EntityCollection):
    ATTRS = {}
    ITEM_CLASS = PropertyDefinition


class RequirementDefinition(Entity):
    ATTRS = dict(
        capability=(String,),

        node=(Pass,),
        relationship=(Pass,),
        occurrences=(Pass,),
    )


class RequirementDefinitionCollection(OrderedEntityCollection):
    ITEM_CLASS = RequirementDefinition


class NodeType(Entity):
    ATTRS = dict(
        artifacts=(ArtifactDefinitionCollection,),
        attributes=(AttributeDefinitionCollection,),
        capabilities=(CapabilityDefinitionCollection,),
        derived_from=(NodeTypeReference,),
        interfaces=(InterfaceDefinitionCollection,),
        properties=(PropertyDefinitionCollection,),
        requirements=(RequirementDefinitionCollection,),

        description=(Pass,),
    )


class NodeTypeCollection(EntityCollection):
    ATTRS = {}
    ITEM_CLASS = NodeType

    def merge(self, other):
        duplicates = set(self.keys()) & set(other.keys())
        if len(duplicates) > 0:
            raise MergeError("Duplicated types: {}".format(duplicates))
        self.update(other)


class RelationshipType(Entity):
    ATTRS = dict(
        derived_from=(String,),
        valid_target_types=(Pass,),
        interfaces=(Pass,),
    )


class RelationshipTypeCollection(EntityCollection):
    ATTRS = {}
    ITEM_CLASS = RelationshipType


class ServiceTemplate(Entity):
    ATTRS = dict(
        node_types=(NodeTypeCollection,),
        relationship_types=(RelationshipTypeCollection,),
        topology_template=(TopologyTemplate,),
        tosca_definitions_version=(String,),
    )
    RECURSE_ON = (
        "node_types",
        "topology_template",
    )

    def is_compatible_with(self, other):
        key = "tosca_definitions_version"
        return self[key] == other[key]

    def merge(self, other):
        if not self.is_compatible_with(other):
            raise MergeError("Incompatible ServiceTemplate versions")

        for key in self.RECURSE_ON:
            if key in self:
                self[key].merge(other[key])
            else:
                self[key] = other[key]

    def resolve(self):
        for k in self.RECURSE_ON:
            self[k].resolve(self)

    def instantiate(self, inputs):
        instances = []
        for name, item in self["topology_template"]["node_templates"].items():
            instances.append(item.instantiate(name, inputs))
        return instances
