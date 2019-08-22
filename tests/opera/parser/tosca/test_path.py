import pathlib

import pytest

from opera.error import ParseError
from opera.parser.tosca.path import Path
from opera.parser.yaml.node import Node


class TestBuild:
    def test_build(self):
        assert isinstance(Path.build(Node("/")).data, pathlib.PurePath)


class TestPrefixPath:
    @pytest.mark.parametrize("input,prefix", [
        ("/a/b", "c"), ("/a", "b"), ("/a", "../.."), ("/c", "."),
    ])
    def test_prefix_absolute_path(self, input, prefix):
        path = Path(pathlib.PurePath(input), None)
        path.prefix_path(pathlib.PurePath(prefix))

        assert str(path.data) == input

    @pytest.mark.parametrize("input,prefix,output", [
        ("a", "b", "b/a"),
        ("a", "..", "../a"),
        ("a", ".", "a"),
        ("a/b", "c", "c/a/b"),
        ("a/b", "..", "../a/b"),
        ("a/b", "c/d", "c/d/a/b"),
        ("a", "c/d/", "c/d/a"),
    ])
    def test_prefix_relative_path(self, input, prefix, output):
        path = Path(pathlib.PurePath(input), None)
        path.prefix_path(pathlib.PurePath(prefix))

        assert str(path.data) == output
