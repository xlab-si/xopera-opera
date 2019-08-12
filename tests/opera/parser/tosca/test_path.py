import pathlib

import pytest

from opera.error import ParseError
from opera.parser.tosca.path import Path
from opera.parser.yaml.node import Node


class TestBuild:
    def test_build(self):
        assert isinstance(Path.build(Node("/")).data, pathlib.PurePath)
