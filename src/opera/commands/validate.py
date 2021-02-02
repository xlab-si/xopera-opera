import argparse
import typing
from pathlib import Path, PurePath
from tempfile import TemporaryDirectory
from zipfile import ZipFile, is_zipfile

import shtab
import yaml
from yaml import YAMLError

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.parser.tosca.csar import CloudServiceArchive


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
        "csar", type=argparse.FileType("r"),
        help="TOSCA YAML service template file or CSAR"
    ).complete = shtab.FILE
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    try:
        inputs = yaml.safe_load(args.inputs) if args.inputs else {}
    except YAMLError as e:
        print("Invalid inputs: {}".format(e))
        return 1

    try:
        if is_zipfile(args.csar.name):
            print("Validating CSAR...")
            validate_compressed_csar(args.csar.name, inputs)
        else:
            print("Validating service template...")
            validate_service_template(args.csar.name, inputs)
        print("Done.")
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def validate_compressed_csar(csar_name: str, inputs: typing.Optional[dict]):
    if inputs is None:
        inputs = {}

    with TemporaryDirectory() as csar_validation_dir:
        csar = CloudServiceArchive.create(PurePath(csar_name))
        csar.validate_csar()
        tosca_service_template = csar.get_entrypoint()

        # unzip csar to temporary folder
        ZipFile(csar_name, "r").extractall(csar_validation_dir)

        # try to initiate service template from csar
        ast = tosca.load(Path(csar_validation_dir), Path(tosca_service_template))
        ast.get_template(inputs)


def validate_service_template(service_template: str, inputs: typing.Optional[dict]):
    if inputs is None:
        inputs = {}
    ast = tosca.load(Path.cwd(), PurePath(service_template))
    ast.get_template(inputs)
