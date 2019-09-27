import pkg_resources

from opera.parser import yaml


def load(version):
    return yaml.load(
        pkg_resources.resource_stream("{}.{}".format(__package__, version), version + ".yaml"),
        "STDLIB[{}]".format(version),
    )
