import argparse
import yaml
import shtab

from os import path
from pathlib import Path, PurePath
from typing import Optional

from opera.error import DataError, ParseError, OperaError
from opera.parser import tosca
from opera.parser.tosca.csar import CloudServiceArchive
from opera.storage import Storage
from opera.utils import format_outputs


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "info",
        help="Show information about the current project"
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
    parser.add_argument(
        "csar_or_rootdir", nargs='?',
        help="Path to a packed or unpacked CSAR. "
             "Defaults to the current directory if not specified.",
    ).complete = shtab.DIR
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {0} is not a valid path!"
                                         .format(args.instance_path))

    storage = Storage.create(args.instance_path)
    try:
        outs = info(args.csar_or_rootdir, storage)
        print(format_outputs(outs, args.format))
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1
    return 0


def info(csar_or_rootdir: Optional[PurePath], storage: Storage) -> dict:
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

    # stateless autodetect first if possible,
    # which can then be overwritten via state
    if csar_or_rootdir is not None:
        csar = CloudServiceArchive.create(csar_or_rootdir)
        try:
            csar.validate_csar()
            info_dict["content_root"] = csar_or_rootdir

            meta = csar.parse_csar_meta()
            if meta is not None:
                info_dict["service_template"] = meta.entry_definitions
        except OperaError:
            pass

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
