import argparse
from os import path
from pathlib import PurePath
from typing import Dict

import shtab
from opera_tosca_parser.commands.parse import parse_service_template

from opera.error import DataError, ParseError
from opera.storage import Storage
from opera.utils import format_outputs, save_outputs
from opera.instance.topology import Topology


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "outputs",
        help="Retrieve deployment outputs (from TOSCA service template)"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help="Storage folder location (instead of default .opera)"
    ).complete = shtab.DIR
    parser.add_argument(
        "--format", "-f", choices=("yaml", "json"), type=str, default="yaml",
        help="Output format",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file location"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Turns on verbose mode",
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError(f"Directory {args.instance_path} is not a valid path!")

    storage = Storage.create(args.instance_path)

    try:
        outs = outputs(storage)
        if args.output:
            save_outputs(outs, args.format, args.output)
        else:
            print(format_outputs(outs, args.format).strip())
    except ParseError as e:
        print(f"{e.loc}: {e}")
        return 1
    except DataError as e:
        print(str(e))
        return 1
    return 0


def outputs(storage: Storage) -> dict:
    """
    Get deployment outputs.

    :raises ParseError:
    :raises DataError:
    """
    if storage.exists("inputs"):
        inputs = storage.read_json("inputs")
    else:
        inputs = {}

    if storage.exists("root_file"):
        service_template_path = PurePath(storage.read("root_file"))

        template, _ = parse_service_template(service_template_path, inputs)
        # We need to instantiate the template in order
        # to get access to the instance state.
        topology = Topology.instantiate(template, storage)
        result: Dict = topology.get_outputs()
        return result
    else:
        print("There is no root_file in storage.")
        return {}
