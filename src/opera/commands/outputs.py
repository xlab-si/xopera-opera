import argparse
import shtab

from os import path
from pathlib import Path, PurePath

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage
from opera.utils import format_outputs


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "outputs",
        help="Retrieve service template outputs"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help=".opera storage folder location"
    ).complete = shtab.DIR
    parser.add_argument(
        "--format", "-f", choices=("yaml", "json"), type=str,
        default="yaml", help="Output format",
    )
    parser.add_argument(
        "--verbose", "-v", action='store_true',
        help="Turns on verbose mode",
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {} is not a valid path!"
                                         .format(args.instance_path))

    storage = Storage.create(args.instance_path)

    try:
        outs = outputs(storage)
        print(format_outputs(outs, args.format))
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1
    return 0


def outputs(storage: Storage) -> dict:
    """
    :raises ParseError:
    :raises DataError:
    """
    if storage.exists("inputs"):
        inputs = storage.read_json("inputs")
    else:
        inputs = {}

    if storage.exists("root_file"):
        service_template = storage.read("root_file")

        if storage.exists("csars"):
            csar_dir = Path(storage.path) / "csars" / "csar"
            ast = tosca.load(Path(csar_dir),
                             PurePath(service_template).relative_to(csar_dir))
        else:
            ast = tosca.load(Path.cwd(), PurePath(service_template))

        template = ast.get_template(inputs)
        # We need to instantiate the template in order
        # to get access to the instance state.
        template.instantiate(storage)
        return template.get_outputs()
    else:
        print("There is no root_file in storage.")
        return {}
