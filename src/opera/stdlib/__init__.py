import pkg_resources

from opera.parser import yaml
from opera.parser.yaml import Node


def load(version: str) -> Node:
    return yaml.load(
        pkg_resources.resource_stream(__name__, version + ".yaml"),
        "STD[{}]".format(version),
    )
