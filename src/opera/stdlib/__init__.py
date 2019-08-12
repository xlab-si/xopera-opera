import pkg_resources

from opera.parser import yaml


def load(version):
    return yaml.load(
        pkg_resources.resource_stream(__name__, version + ".yaml"),
        "STD[{}]".format(version),
    )
