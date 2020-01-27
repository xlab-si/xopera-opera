import pytest

from opera.error import ParseError
from opera.parser.tosca.base import Base
from opera.parser.tosca.entity import Entity, TypeEntity
from opera.parser.tosca.reference import Reference
from opera.parser.yaml.node import Node


class DummyAttr(Base):
    pass


class DummyEntity(Entity):
    ATTRS = dict(
        required=DummyAttr,
        optional=DummyAttr,
    )
    REQUIRED = {"required"}


class TestEntityValidate:
    @pytest.mark.parametrize("data", [1, 3.4, "", "a", (), []])
    def test_non_dict_data_is_invalid(self, data):
        with pytest.raises(ParseError):
            DummyEntity.validate(Node(data))

    @pytest.mark.parametrize("key", [1, 3.4, False, None, (), []])
    def test_non_string_keys_are_invalid(self, key):
        with pytest.raises(ParseError):
            DummyEntity.validate(Node(key))

    def test_non_declared_attrs_fail(self):
        with pytest.raises(ParseError, match="non_declared_attr"):
            DummyEntity.validate(Node({
                Node("required"): Node("value"),
                Node("non_declared_attr"): Node(3),
            }))

    def test_required_attrs(self):
        with pytest.raises(ParseError, match="required"):
            DummyEntity.validate(Node({}))

    def test_ok_if_optional_is_missing(self):
        DummyEntity.validate(Node({
            Node("required"): Node("value"),
        }))


class TestEntityBuild:
    def test_build_attrs(self):
        obj = DummyEntity.build(Node({
            Node("required"): Node(3),
            Node("optional"): Node(2),
        }))

        assert isinstance(obj, DummyEntity)
        assert isinstance(obj.data["required"], DummyAttr)
        assert isinstance(obj.data["optional"], DummyAttr)


class TestEntityAttrs:
    def test_attrs(self):
        assert DummyEntity.attrs() == DummyEntity.ATTRS


class TestEntityGetattr:
    def test_get_valid_attr(self):
        assert Entity(dict(a=2), None).a == 2

    def test_get_invalid_attr(self):
        with pytest.raises(AttributeError):
            Entity(dict(a=2), None).b


class TestEntityGetitem:
    def test_get_valid_item(self):
        assert Entity(dict(a=2), None)["a"] == 2

    def test_get_invalid_item(self):
        with pytest.raises(KeyError):
            Entity(dict(a=2), None)["b"]


class TestEntityIteration:
    def test_iteration(self):
        assert set(Entity(dict(a=1, b=2, c="d"), None)) == {"a", "b", "c"}


class TestEntityDig:
    def test_dig_through_dict(self):
        obj = Entity({
            "a": 1,
            "b": 2,
            "c": Entity({
                "d": 6,
                "e": 7,
            }, None),
        }, None)

        assert obj.dig("a") == 1
        assert obj.dig("c", "d") == 6

    def test_dig_for_missing_key(self):
        obj = Entity({
            "a": 1,
            "b": 2,
            "c": Entity({
                "d": 6,
                "e": 7,
            }, None),
        }, None)

        assert obj.dig("k") is None
        assert obj.dig("c", "k") is None


class TestEntityItems:
    def test_items(self):
        obj = Entity(dict(a=1, b=2), None)

        assert {("a", 1), ("b", 2)} == set(obj.items())


class TestEntityValues:
    def test_values(self):
        obj = DummyEntity(dict(a=1, b=2, c=3), None)

        assert {1, 2, 3} == set(obj.values())


class Goodie(TypeEntity):
    REFERENCE = Reference("path")
    ATTRS = dict(dummy=Base)


class Baddie(TypeEntity):
    ATTRS = dict(dummy=Base)


class TestTypeEntityValidate:
    def test_valid_data(self, yaml_ast):
        Goodie.validate(yaml_ast(
            """
            derived_from: my_parent_type
            description: My type description
            metadata: {}
            version: 1.2.3.go-4
            """
        ))

    def test_missing_derived_from(self, yaml_ast):
        with pytest.raises(ParseError):
            Goodie.validate(yaml_ast(
                """
                description: My type description
                metadata: {}
                version: 1.2.3.go-4
                """
            ))


class TestTypeEntityAttrs:
    def test_field_addition(self):
        assert set(Goodie.attrs().keys()) == {
            "derived_from", "description", "metadata", "version", "dummy"
        }

    def test_reference_class_check(self):
        with pytest.raises(AssertionError):
            Baddie.attrs()
