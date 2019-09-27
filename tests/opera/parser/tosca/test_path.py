import pathlib

from opera.parser.tosca.path import ToscaPath
from opera.parser.yaml.node import Node


class TestBuild:
    def test_build(self):
        assert isinstance(ToscaPath.build(Node("/")).data, pathlib.PurePath)
