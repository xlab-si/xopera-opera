from typing import Optional, Set, Dict, Type, Union

from .base import Base
from .list import List
from .map import Map, MapWrapper
from .reference import Reference, ReferenceXOR
from .string import String
from .version import Version


class Entity(MapWrapper):
    # This must be overridden in derived classes
    ATTRS: Dict[str, Union[Type[Base], Base, Map, List, Reference, ReferenceXOR]] = {}

    # This can be overridden in derived classes
    REQUIRED: Set[str] = set()

    @classmethod
    def validate(cls, yaml_node):
        if cls.ATTRS == {}:
            raise AssertionError()
        if not isinstance(cls.REQUIRED, set):
            raise AssertionError()

        if not isinstance(yaml_node.value, dict):
            cls.abort("Expected map.", yaml_node.loc)

        data_keys = set()
        for k in yaml_node.value:
            if not isinstance(k.value, str):
                cls.abort("Expected string", k.loc)
            data_keys.add(k.value)

        missing_keys = cls.REQUIRED - data_keys
        if missing_keys:
            cls.abort("Missing required fields: {}".format(", ".join(missing_keys)), yaml_node.loc)

        extra_keys = data_keys - cls.attrs().keys()
        if extra_keys:
            cls.abort("Invalid keys: {}".format(", ".join(extra_keys)), yaml_node.loc)

    @classmethod
    def build(cls, yaml_node):
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
        except KeyError as e:
            raise AttributeError(key) from e


class TypeEntity(Entity):
    REFERENCE: Optional[Reference] = None  # Override in subclasses

    @classmethod
    def validate(cls, yaml_node):
        super().validate(yaml_node)
        for key in yaml_node.value:
            if key.value == "derived_from":
                return
        cls.abort("Type is missing derived_from key.", yaml_node.loc)

    @classmethod
    def attrs(cls):
        if not isinstance(cls.REFERENCE, Reference):
            raise AssertionError("Override REFERENCE in {} with Reference.".format(cls.__name__))

        attributes = cls.ATTRS.copy()
        attributes.update(
            derived_from=cls.REFERENCE,
            description=String,
            metadata=Map(String),
            version=Version,
        )
        return attributes
