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
    parser.add_argument(
        "--workers", "-w",
        help="Maximum number of concurrent undeployment \
            threads (positive number, default 1)",
        type=int, default=1
    )
    parser.set_defaults(func=undeploy)


def undeploy(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {0} is not a valid path!".format(args.instance_path))

    storage = Storage(Path(args.instance_path)) if args.instance_path else Storage(Path(".opera"))
    root = storage.read("root_file")
    inputs = storage.read_json("inputs")

    if args.workers < 1:
        print("{0} is not a positive number!".format(args.workers))
        return 1

    try:
        ast = tosca.load(Path.cwd(), PurePath(root))
        template = ast.get_template(inputs)
        topology = template.instantiate(storage)
        topology.undeploy(args.workers)
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0
