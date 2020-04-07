import argparse
from pathlib import Path, PurePath

import yaml
from opera.error import ParseError
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
    parser.add_argument("csar",
                        type=argparse.FileType("r"),
                        help="Cloud service archive file")
    parser.set_defaults(func=validate)


def validate(args):
    print("Validating service template ...")

    try:
        inputs = yaml.safe_load(args.inputs) if args.inputs else {}
    except Exception as e:
        print("Invalid inputs: {}".format(e))
        return 1

    try:
        ast = tosca.load(Path.cwd(), PurePath(args.csar.name))
        ast.get_template(inputs)
        print("Done.")
        return 0
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
