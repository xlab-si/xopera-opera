import argparse
from pathlib import Path, PurePath

import json
import yaml

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage
from os import path


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "outputs",
        help="Retrieve service template outputs"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help=".opera storage folder location"
    )
    parser.add_argument(
        "--format", "-f", choices=("yaml", "json"), type=str,
        default="yaml", help="Output format",
    )
    parser.set_defaults(func=outputs)


def outputs(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {0} is not a valid path!".format(args.instance_path))

    storage = Storage(Path(args.instance_path)) if args.instance_path else Storage(Path(".opera"))
    root = storage.read("root_file")
    inputs = storage.read_json("inputs")

    try:
        ast = tosca.load(Path.cwd(), PurePath(root))
        template = ast.get_template(inputs)
        topology = template.instantiate(storage)
        # We need to instantiate the template in order to get access to the
        # instance state.
        print(format_outputs(template.get_outputs(), args.format))
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def format_outputs(outputs, format):
    if format == "json":
        return json.dumps(outputs, indent=2)
    if format == "yaml":
        return yaml.safe_dump(outputs, default_flow_style=False)

    assert False, "BUG - invalid format"
