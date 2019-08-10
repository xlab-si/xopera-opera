import pytest

from opera.parser.tosca.reference import Reference
from opera.parser.yaml.node import Node


class TestReferenceInit:
    @pytest.mark.parametrize("path", [
        ("single",), ("multi", "path"), ("a", "b", "c", "d"),
    ])
    def test_valid_init(self, path):
        assert Reference(*path).section_path == path

    def test_empty_path(self):
        with pytest.raises(AssertionError):
            Reference()

    @pytest.mark.parametrize("path", [
        (1,), (2.3,), (False,), ((),), ([],), ({},), ("a", 1),
    ])
    def test_invalid_path_components(self, path):
        with pytest.raises(AssertionError):
            Reference(*path)


class TestReferenceParse:
    @pytest.mark.parametrize("path", [
        ("single",), ("multi", "path"), ("a", "b", "c", "d"),
    ])
    def test_parse(self, path):
        assert Reference(*path).parse(Node("name")).section_path == path
