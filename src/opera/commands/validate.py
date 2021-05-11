import argparse
import typing
from pathlib import Path, PurePath
from tempfile import TemporaryDirectory
from zipfile import is_zipfile

import shtab
import yaml
from yaml import YAMLError

from opera.error import OperaError, ParseError
from opera.parser import tosca
from opera.parser.tosca.csar import CloudServiceArchive, DirCloudServiceArchive


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "validate",
        help="Validate TOSCA service template or CSAR"
    )
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="YAML or JSON file with inputs",
    ).complete = shtab.FILE
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Turns on verbose mode",
    )
    parser.add_argument(
        "csar_or_service_template", type=str, nargs="?",
        help="TOSCA YAML service template file or CSAR"
    ).complete = shtab.FILE
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    try:
        inputs = yaml.safe_load(args.inputs) if args.inputs else {}
    except YAMLError as e:
        print("Invalid inputs: {}".format(e))
        return 1

    if args.csar_or_service_template is None:
        csar_or_st_path = PurePath(".")
    else:
        csar_or_st_path = PurePath(args.csar_or_service_template)

    try:
        if is_zipfile(csar_or_st_path) or Path(csar_or_st_path).is_dir():
            print("Validating CSAR...")
            validate_csar(csar_or_st_path, inputs)
        else:
            print("Validating service template...")
            validate_service_template(csar_or_st_path, inputs)
        print("Done.")
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except OperaError as e:
        print(str(e))
        return 1

    return 0


def validate_csar(csar_path: PurePath, inputs: typing.Optional[dict]):
    if inputs is None:
        inputs = {}

    csar = CloudServiceArchive.create(csar_path)
    csar.validate_csar()
    entrypoint = csar.get_entrypoint()

    if entrypoint is not None:
        if isinstance(csar, DirCloudServiceArchive):
            validate_service_template(csar_path / entrypoint, inputs)
        else:
            with TemporaryDirectory() as csar_validation_dir:
                csar.unpackage_csar(csar_validation_dir)
                validate_service_template(PurePath(csar_validation_dir) / entrypoint, inputs)


def validate_service_template(service_template: PurePath, inputs: typing.Optional[dict]):
    if inputs is None:
        inputs = {}
    ast = tosca.load(Path(service_template.parent), PurePath(service_template.name))
    ast.get_template(inputs)
