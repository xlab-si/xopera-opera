import pkg_resources

import yaml


def load():
    return yaml.safe_load(
        pkg_resources.resource_stream(__name__, "types.yaml"),
    )
