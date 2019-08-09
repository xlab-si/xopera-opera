import pytest

from opera.error import ParseError
from opera.parser.tosca.base import Base
from opera.parser.utils.location import Location
from opera.parser.yaml.node import Node


class TestParse:
    @pytest.mark.parametrize(
        "data", ["", 4, "a", (), (1, 2, 3), [], ["a", "b"]],
    )
    def test_creates_new_instance(self, data):
        obj = Base.parse(Node(data, Location("s", 1, 2)))

        assert obj.data == data
        assert obj.loc.stream_name == "s"
        assert obj.loc.line == 1
        assert obj.loc.column == 2


class TestNormalize:
    @pytest.mark.parametrize(
        "data", ["", 4, "a", (), (1, 2, 3), [], ["a", "b"]],
    )
    def test_normalize_is_noop(self, data):
        assert Base.normalize(data) == data


class TestValidate:
    @pytest.mark.parametrize(
        "data", ["", 4, "a", (), (1, 2, 3), [], ["a", "b"]],
    )
    def test_validate_is_always_ok(self, data):
        Base.validate(data)


class TestBuild:
    @pytest.mark.parametrize(
        "data", ["", 4, "a", (), (1, 2, 3), [], ["a", "b"]],
    )
    def test_build_creates_new_instance(self, data):
        obj = Base.build(Node(data, Location("stream", 1, 2)))

        assert obj.data == data
        assert obj.loc.stream_name == "stream"
        assert obj.loc.line == 1
        assert obj.loc.column == 2


class TestAbort:
    def test_abort(self):
        with pytest.raises(ParseError, match="Error MsG"):
            Base.abort("Error MsG", None)


class TestBare:
    @pytest.mark.parametrize(
        "data", ["", 4, "a", (), (1, 2, 3), [], ["a", "b"]],
    )
    def test_bare(self, data):
        assert Base(data, None).bare == data


class TestStr:
    @pytest.mark.parametrize("data", [1, 2.3, True, "abc", {}, []])
    def test_str(self, data):
        assert str(data) == str(Base(data, Location("s", 4, 5)))
