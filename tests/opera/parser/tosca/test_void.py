import pytest

from opera.parser.tosca.void import Void
from opera.parser.utils.location import Location


class TestBare:
    @pytest.mark.parametrize("data", [1, 2.3, False, "string", None])
    def test_bare_simple(self, data):
        assert Void(data, Location("path", 2, 3)).bare == data

    def test_bare_dict(self, yaml_ast):
        assert Void.parse(yaml_ast("a: b\nc: 4")).bare == dict(a="b", c=4)

    def test_bare_list(self, yaml_ast):
        assert Void.parse(yaml_ast("[ 1, 2, 3 ]")).bare == [1, 2, 3]
