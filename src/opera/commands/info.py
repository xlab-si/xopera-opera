import argparse
import json
from os import path
from pathlib import Path, PurePath

import yaml

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "info",
        help="Show information about the current project"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help=".opera storage folder location"
    )
    parser.add_argument(
        "--format", "-f", choices=("yaml", "json"), type=str,
        default="yaml", help="Output format",
    )
    parser.add_argument(
        "--verbose", "-v", action='store_true',
        help="Turns on verbose mode",
    )
    parser.set_defaults(func=_parser_callback)


def format_outputs(info, format):
    if format == "json":
        return json.dumps(info, indent=2)
    if format == "yaml":
        return yaml.safe_dump(info, default_flow_style=False)

    assert False, "BUG - an invalid format got past the parser"


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {0} is not a valid path!"
                                         .format(args.instance_path))

    storage = Storage.create(args.instance_path)
    try:
        outs = info(storage)
        print(format_outputs(outs, args.format))
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1
    return 0


def info(storage: Storage) -> dict:
    """
    :raises ParseError:
    :raises DataError:
    """
    info_dict = dict(
        service_template=None,
        content_root=None,
        inputs=None,
        status=None
    )

    if storage.exists("root_file"):
        service_template = storage.read("root_file")
        info_dict["service_template"] = service_template

        if storage.exists("inputs"):
            info_dict["inputs"] = str(storage.path / "inputs")
            inputs = yaml.safe_load(storage.read("inputs"))
        else:
            inputs = {}

        if storage.exists("csars/csar"):
            csar_dir = Path(storage.path) / "csars" / "csar"
            info_dict["content_root"] = str(csar_dir)
            ast = tosca.load(Path(csar_dir),
                             PurePath(service_template).relative_to(csar_dir))
        else:
            ast = tosca.load(Path.cwd(), PurePath(service_template))

        if storage.exists("instances"):
            template = ast.get_template(inputs)
            # We need to instantiate the template in order
            # to get access to the instance state.
            topology = template.instantiate(storage)
            info_dict["status"] = topology.get_info()
        else:
            info_dict["status"] = "initialized"

    return info_dict
