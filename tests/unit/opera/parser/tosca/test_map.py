from unittest.mock import Mock

import pytest

from opera.error import ParseError
from opera.parser.tosca.map import Map, MapWrapper, OrderedMap
from opera.parser.tosca.base import Base
from opera.parser.yaml.node import Node


class TestMapWrapperGetitem:
    def test_lut_access_for_string_key(self):
        assert MapWrapper({"k": "v"}, None)["k"] == "v"

    def test_test_non_string_key(self):
        with pytest.raises(KeyError):
            assert MapWrapper({Base(1, None): "v" }, None)[1]


class TestMapWrapperIteration:
    def test_iteration(self):
        data = dict(a="b", c="d")
        assert list(MapWrapper(data, None)) == list(data)


class TestMapWrapperValues:
    def test_values(self):
        data = dict(a="b", c="d")
        assert list(MapWrapper(data, None).values()) == list(data.values())


class TestMapWrapperKeys:
    def test_keys(self):
        data = dict(a="b", c="d")
        assert list(MapWrapper(data, None).keys()) == list(data.keys())


class TestMapWrapperItems:
    def test_items(self):
        data = dict(a="b", c="d")
        assert list(MapWrapper(data, None).items()) == list(data.items())


class TestMapWrapperDig:
    def test_single_level(self):
        assert MapWrapper({"k": "v" }, None).dig("k") == "v"

    def test_multi_level(self):
        obj = MapWrapper({
            "a": MapWrapper({"b": "c"}, None),
            "d": MapWrapper({"e": "f"}, None),
        }, None)

        assert obj.dig("a", "b") == "c"
        assert obj.dig("d", "e") == "f"

    def test_bad_index(self):
        assert MapWrapper({}, None).dig("a") is None

    def test_bad_index_type(self):
        assert MapWrapper({}, None).dig(1) is None


class TestMapWrapperMerge:
    def test_merge(self):
        map = MapWrapper({"a": 0}, None)
        map.merge(MapWrapper({"b": 1}, None))

        assert map.data == dict(a=0, b=1)

    def test_duplicated_key(self):
        with pytest.raises(ParseError, match="twice"):
            MapWrapper({"twice": 0}, None).merge(
                MapWrapper({"twice": 1}, None),
            )


class TestMapParse:
    @pytest.mark.parametrize("data", [1, 3.4, "", "a", (), []])
    def test_non_dict_data_is_invalid(self, data):
        with pytest.raises(ParseError, match="map"):
            Map(Base).parse(Node(data))

    def test_empty_dict_is_ok(self):
        assert Map(Base).parse(Node({})).data == {}

    def test_dict_is_ok(self):
        obj = Map(Base).parse(Node({
            Node("a"): Node("b"),
        }))

        assert len(obj.data) == 1
        assert obj.data["a"].data == "b"


class TestOrderedMapParse:
    @pytest.mark.parametrize("data", [1, 3.4, "", "a", (), {}])
    def test_non_list_data_is_invalid(self, data):
        with pytest.raises(ParseError, match="list"):
            OrderedMap(Base).parse(Node(data))

    def test_empty_list_is_ok(self):
        assert OrderedMap(Base).parse(Node([])).data == {}

    def test_dict_is_ok(self):
        obj = OrderedMap(Base).parse(Node([
            Node({Node("a"): Node("b")}),
            Node({Node("c"): Node("d")}),
        ]))
        data = [(k, v.data) for k, v in obj.data.items()]

        assert data == [("a", "b"), ("c", "d")]


class TestMapWrapperVisit:
    def test_empty_visit(self):
        MapWrapper({}, None).visit("called", "with", keyword="args")

    def test_visit(self):
        obj1 = Base(None, None)
        obj1.called = Mock()
        obj2 = Base(None, None)
        obj2.not_called = Mock()

        MapWrapper({"a": obj1, "b": obj2}, None).visit(
            "called", "with", keyword="args",
        )

        obj1.called.assert_called_once_with("with", keyword="args")
        obj2.not_called.assert_not_called()
