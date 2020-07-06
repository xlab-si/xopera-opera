import argparse
import typing
from pathlib import Path, PurePath

import yaml

from opera.error import ParseError, DataError
from opera.parser import tosca


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "validate",
        help="Validate service template from CSAR"
    )
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="YAML file with inputs",
    )
    parser.add_argument(
        "--verbose", "-v", action='store_true',
        help="Turns on verbose mode",
    )
    parser.add_argument("csar",
                        type=argparse.FileType("r"),
                        help="Cloud service archive file")
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    print("Validating service template ...")

    try:
        inputs = yaml.safe_load(args.inputs) if args.inputs else {}
    except Exception as e:
        print("Invalid inputs: {}".format(e))
        return 1

    try:
        validate(args.csar.name, inputs)
        print("Done.")
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def validate(service_template: str, inputs: typing.Optional[dict]):
    if inputs is None:
        inputs = {}
    ast = tosca.load(Path.cwd(), PurePath(service_template))
    ast.get_template(inputs)
