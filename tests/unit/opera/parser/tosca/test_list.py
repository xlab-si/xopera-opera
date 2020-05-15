from unittest.mock import Mock

import pytest

from opera.error import ParseError
from opera.parser.tosca.list import List, ListWrapper
from opera.parser.tosca.base import Base
from opera.parser.yaml.node import Node


class TestListParse:
    @pytest.mark.parametrize("data", [1, 3.4, "", "a", (), {}])
    def test_non_list_data_is_invalid(self, data):
        with pytest.raises(ParseError, match="list"):
            List(Base).parse(Node(data))

    def test_empty_list_is_ok(self):
        assert List(Base).parse(Node([])).data == []

    def test_list_is_ok(self):
        obj = List(Base).parse(Node([Node("a"), Node("b")]))

        assert len(obj.data) == 2
        assert obj.data[0].data == "a"
        assert obj.data[1].data == "b"


class TestListWrapperGetitem:
    def test_getitem(self):
        assert ListWrapper(["a", "b"], None)[1] == "b"

    def test_getitem_invalid_index(self):
        with pytest.raises(IndexError):
            ListWrapper([], None)[1]

    def test_getitem_invalid_index_type(self):
        with pytest.raises(TypeError):
            ListWrapper([], None)["a"]


class TestListWrapperIteration:
    def test_iteration(self):
        assert tuple(ListWrapper(["a", "b"], None)) == ("a", "b")

class TestListWrapperDig:
    def test_single_level(self):
        assert ListWrapper(["a", "b"], None).dig(1) == "b"

    def test_multi_level(self):
        obj = ListWrapper([
            ListWrapper(["a", "b"], None),
            ListWrapper(["c", "d"], None),
        ], None)

        assert obj.dig(0, 0) == "a"
        assert obj.dig(0, 1) == "b"
        assert obj.dig(1, 0) == "c"
        assert obj.dig(1, 1) == "d"

    def test_bad_index(self):
        assert ListWrapper([], None).dig(1) is None

    def test_bad_index_type(self):
        assert ListWrapper([], None).dig("a") is None


class TestListWrapperVisit:
    def test_empty_visit(self):
        ListWrapper([], None).visit("called", "with", keyword="args")

    def test_non_empty_visit(self):
        obj1 = Base(None, None)
        obj1.called = Mock()
        obj2 = Base(None, None)
        obj2.not_called = Mock()

        ListWrapper([obj1, obj2], None).visit("called", "with", keyword="args")

        obj1.called.assert_called_once_with("with", keyword="args")
        obj2.not_called.assert_not_called()
