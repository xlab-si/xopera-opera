import pkg_resources

from opera.parser import yaml
from opera.parser.yaml import Node


def load(version: str) -> Node:
    return yaml.load(
        pkg_resources.resource_stream("{}.{}".format(__package__, version), version + ".yaml"),
        "STDLIB[{}]".format(version),
    )
