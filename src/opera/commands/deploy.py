import argparse
from pathlib import Path, PurePath

import yaml

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "deploy",
        help="Deploy service template from CSAR"
    )
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="YAML file with inputs",
    )
    parser.add_argument("csar",
                        type=argparse.FileType("r"),
                        help="cloud service archive file")
    parser.set_defaults(func=deploy)


def deploy(args):
    storage = Storage(Path(".opera"))
    storage.write(args.csar.name, "root_file")

    # TODO(@tadeboro): This should be part of the init command that we do not
    # have yet.
    try:
        inputs = yaml.safe_load(args.inputs) if args.inputs else {}
        storage.write_json(inputs, "inputs")
    except Exception as e:
        print("Invalid inputs: {}".format(e))
        return 1

    try:
        ast = tosca.load(Path.cwd(), PurePath(args.csar.name))
        template = ast.get_template(inputs)
        topology = template.instantiate(storage)
        topology.deploy()
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0
