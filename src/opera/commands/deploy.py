import argparse
from pathlib import Path, PurePath

import yaml

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage
from os import path


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "deploy",
        help="Deploy service template from CSAR"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help=".opera storage folder location"
    )
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="Optional: YAML file with inputs to override the inputs supplied in init",
    )
    parser.add_argument(
        "--workers", "-w",
        help="Maximum number of concurrent deployment \
            threads (positive number, default 1)",
        type=int, default=1
    )
    parser.add_argument("template",
                        type=argparse.FileType("r"), nargs='?',
                        help="TOSCA YAML service template file",
                        )
    parser.set_defaults(func=deploy)


def deploy(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {0} is not a valid path!".format(args.instance_path))

    storage = Storage(Path(args.instance_path)) if args.instance_path else Storage(Path(".opera"))

    if args.workers < 1:
        print("{0} is not a positive number!".format(args.workers))
        return 1

    # TODO(@tadeboro): This should be part of the init command that we do not
    # have yet.
    if args.template:
        storage.write(args.template.name, "root_file")
        service_template = args.template.name
    else:
        if storage.exists("root_file"):
            service_template = storage.read("root_file")
        else:
            print("CSAR or template root file does not exist. Maybe you have forgotten to initialize it.")
            return 1

    try:
        if storage.exists("inputs"):
            inputs = yaml.safe_load(storage.read("inputs"))
        else:
            inputs = {}
            storage.write_json(inputs, "inputs")

        if args.inputs:
            inputs = yaml.safe_load(args.inputs)
            storage.write_json(inputs, "inputs")

    except Exception as e:
        print("Invalid inputs: {}".format(e))
        return 1

    try:
        ast = tosca.load(Path.cwd(), PurePath(service_template))
        template = ast.get_template(inputs)
        topology = template.instantiate(storage)
        topology.deploy(args.workers)
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0
