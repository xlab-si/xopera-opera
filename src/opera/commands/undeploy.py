import argparse
from pathlib import Path, PurePath

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage
from os import path


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "undeploy",
        help="Undeploy service template"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help=".opera storage folder location"
    )
    parser.set_defaults(func=undeploy)


def undeploy(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {0} is not a valid path!".format(args.instance_path))

    storage = Storage(Path(args.instance_path).joinpath(".opera")) if args.instance_path else Storage(Path(".opera"))
    root = storage.read("root_file")
    inputs = storage.read_json("inputs")

    try:
        ast = tosca.load(Path.cwd(), PurePath(root))
        template = ast.get_template(inputs)
        topology = template.instantiate(storage)
        topology.undeploy()
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0
