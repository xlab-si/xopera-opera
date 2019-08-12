import pathlib

import pytest

from opera.error import ParseError
from opera.parser.tosca.path import Path
from opera.parser.yaml.node import Node


class TestBuild:
    def test_build(self):
        assert isinstance(Path.build(Node("/")).data, pathlib.PurePath)


class TestCanonicalizePaths:
    @pytest.mark.parametrize("input,parent,output", [
        ("/absolute/path", "base/path", "/absolute/path"),
        ("/absolute/path", ".", "/absolute/path"),
        ("rel/path", "base/path", "base/path/rel/path"),
        ("rel/path", ".", "rel/path"),
        ("rel/path", "..", "../rel/path"),
        ("rel/path", "../..", "../../rel/path"),
        ("../rel/path", "component", "rel/path"),
        ("../../rel/path", "component", "../rel/path"),
    ])
    def test_canonicalization(self, input, parent, output):
        path = Path(pathlib.PurePath(input), None)
        path.canonicalize_paths(pathlib.PurePath(parent))

        assert str(path.data) == output
