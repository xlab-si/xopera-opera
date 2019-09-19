from typing import Dict, Set, Union

from opera.parser.tosca.base import Base
from opera.parser.yaml.node import Node
from .map import Map, MapWrapper
from .reference import Reference
from .string import String
from .version import Version


class Entity(MapWrapper):
    ATTRS: Dict[str, Union[Base, Reference]] = {}  # This must be overridden in derived classes
    REQUIRED: Set[str] = set()  # This can be overridden in derived classes

    @classmethod
    def validate(cls, yaml_node: Node):
        assert cls.ATTRS != {}
        assert isinstance(cls.REQUIRED, set)

        if not isinstance(yaml_node.value, dict):
            cls.abort("Expected map.", yaml_node.loc)

        data_keys = set()
        for k in yaml_node.value:
            if not isinstance(k.value, str):
                cls.abort("Expected string", k.loc)
            data_keys.add(k.value)

        missing_keys = cls.REQUIRED - data_keys
        if missing_keys:
            cls.abort(
                "Missing required fields: {}".format(", ".join(missing_keys)),
                yaml_node.loc,
            )

        extra_keys = data_keys - cls.attrs().keys()
        if extra_keys:
            cls.abort(
                "Invalid keys: {}".format(", ".join(extra_keys)),
                yaml_node.loc,
            )

    @classmethod
    def build(cls, yaml_node: Node):
        classes = cls.attrs()
        data = {
            k.value: classes[k.value].parse(v)
            for k, v in yaml_node.value.items()
        }
        return cls(data, yaml_node.loc)

    @classmethod
    def attrs(cls):
        return cls.ATTRS

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise AttributeError(key)


class TypeEntity(Entity):
    REFERENCE: Reference = None  # Override in subclasses

    @classmethod
    def validate(cls, yaml_node: Node):
        super().validate(yaml_node)
        for key in yaml_node.value:
            if key.value == "derived_from":
                return
        cls.abort("Type is missing derived_from key.", yaml_node.loc)

    @classmethod
    def attrs(cls):
        assert isinstance(cls.REFERENCE, Reference), \
            "Override REFERENCE in {} with Reference.".format(cls.__name__)

        attributes = cls.ATTRS.copy()
        attributes.update(
            derived_from=cls.REFERENCE,
            description=String,
            metadata=Map(String),
            version=Version,
        )
        return attributes
