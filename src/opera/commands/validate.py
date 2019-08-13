import argparse
from pathlib import Path, PurePath

from opera import csar
from opera.error import ParseError
from opera.parser import tosca


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "validate",
        help="Validate service template"
    )
    parser.add_argument("template",
                        type=argparse.FileType("r"),
                        help="Service template root")
    parser.set_defaults(func=validate)


def validate(args):
    print("Validating service template ...")
    try:
        tosca.load(Path.cwd(), PurePath(args.template.name))
        print("Done.")
        return 0
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
