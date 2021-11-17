import argparse
from os import path
from pathlib import Path, PurePath
from typing import Dict

import shtab

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage
from opera.utils import format_outputs, save_outputs


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

        if storage.exists("csars"):
            csar_dir = Path(storage.path) / "csars" / "csar"
            ast = tosca.load(Path(csar_dir), service_template_path.relative_to(csar_dir))
        else:
            ast = tosca.load(Path(service_template_path.parent), PurePath(service_template_path.name))

        template = ast.get_template(inputs)
        # We need to instantiate the template in order
        # to get access to the instance state.
        template.instantiate(storage)
        result: Dict = template.get_outputs()
        return result
    else:
        print("There is no root_file in storage.")
        return {}
