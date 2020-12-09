from pathlib import PurePath
import importlib

from opera import stdlib
from opera.error import ParseError
from opera.parser import yaml


SUPPORTED_VERSIONS = dict(
    tosca_simple_yaml_1_3="v_1_3",
)


def load(base_path, template_name):
    with (base_path / template_name).open() as input_fd:
        input_yaml = yaml.load(input_fd, str(template_name))
    if not isinstance(input_yaml.value, dict):
        raise ParseError(
            "Top level structure should be a map.", yaml_node.loc,
        )

    tosca_version = _get_tosca_version(input_yaml)
    parser = _get_parser(tosca_version)

    stdlib_yaml = stdlib.load(tosca_version)
    service = parser.parse(
        stdlib_yaml, base_path, PurePath("STDLIB"), set(),
    )[0]
    service.merge(parser.parse(
        input_yaml, base_path, template_name, set(),
    )[0])
    service.visit("resolve_path", base_path)
    service.visit("resolve_reference", service)

    return service


def _get_parser(tosca_version):
    return importlib.import_module(".v_1_3", __name__).Parser


def _get_tosca_version(input_yaml):
    for k, v in input_yaml.value.items():
        if k.value == "tosca_definitions_version":
            try:
                return SUPPORTED_VERSIONS[v.value]
            except (TypeError, KeyError):
                raise ParseError(
                    "Invalid TOSCA version. Available: {}.".format(
                        ", ".join(SUPPORTED_VERSIONS.keys()),
                    ), v.loc,
                )

    raise ParseError("Missing TOSCA version", input_yaml.loc)
