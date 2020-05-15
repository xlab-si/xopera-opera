import pytest

from opera.parser.tosca.comparable import Comparable


class TestEquality:
    @pytest.mark.parametrize("data", [1, 2.3, "abc", (), [], {}])
    def test_ok(self, data):
        assert Comparable(data, None) == Comparable(data, None)

    @pytest.mark.parametrize("data", [1, 2.3, "abc", (), [], {}])
    def test_not_ok(self, data):
        assert Comparable(data, None) != Comparable("NOT EQUAL", None)


class TestHash:
    @pytest.mark.parametrize("data", [1, 2.3, "abc", ()])
    def test_ok(self, data):
        assert hash(Comparable(data, None)) == hash(Comparable(data, None))
