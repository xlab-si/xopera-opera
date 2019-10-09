import pathlib

import pytest

from opera.error import ParseError
from opera.parser.tosca.path import ToscaPath
from opera.parser.yaml.node import Node


class TestBuild:
    @pytest.mark.parametrize("path", ["a.file", "../a.file", "b/../a.file"])
    def test_build_relative(self, path):
        assert isinstance(ToscaPath.build(Node(path)).data, pathlib.PurePath)

    @pytest.mark.parametrize("path", ["/etc", "/etc/hosts", "/dev/zero", "/doesnotexist", "/does/not/exist"])
    def test_build_absolute(self, path):
        with pytest.raises(ParseError):
            ToscaPath.build(Node(path))
