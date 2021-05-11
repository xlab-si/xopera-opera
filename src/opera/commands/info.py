import argparse
from os import path
from pathlib import Path, PurePath
from typing import Dict, Optional, Union

import shtab
import yaml

from opera.error import DataError, ParseError, OperaError
from opera.parser import tosca
from opera.parser.tosca.csar import CloudServiceArchive
from opera.storage import Storage
from opera.utils import format_outputs, save_outputs


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "info",
        help="Show information about the current project"
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
    parser.add_argument(
        "csar_or_rootdir", nargs="?",
        help="Path to a packed or unpacked TOSCA CSAR (defaults to the current directory if not specified)",
    ).complete = shtab.DIR
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {0} is not a valid path!".format(args.instance_path))

    storage = Storage.create(args.instance_path)
    try:
        if args.csar_or_rootdir is None:
            csar_path = "."
        else:
            csar_path = args.csar_or_rootdir

        outs = info(PurePath(csar_path), storage)
        if args.output:
            save_outputs(outs, args.format, args.output)
        else:
            print(format_outputs(outs, args.format))
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1
    return 0


def info(csar_or_rootdir: Optional[PurePath], storage: Storage) -> dict:
    info_dict: Dict[str, Optional[Union[str, dict, bool]]] = dict(
        service_template=None,
        content_root=None,
        inputs=None,
        status=None,
        csar_metadata=None,
        service_template_metadata=None,
        csar_valid=None
    )

    # stateless autodetect first if possible,
    # which can then be overwritten via state
    if csar_or_rootdir is not None:
        csar = CloudServiceArchive.create(csar_or_rootdir)
        try:
            # this validates CSAR and the entrypoint's (if it exists) metadata
            # failure to validate here means no static information will be available at all
            csar.validate_csar()

            info_dict["content_root"] = str(csar_or_rootdir)
            if csar.get_entrypoint() is not None:
                info_dict["service_template"] = str(csar.get_entrypoint())

                service_template_meta = csar.parse_service_template_meta(csar.get_entrypoint())
                info_dict["service_template_metadata"] = service_template_meta

            csar_meta = csar.parse_csar_meta()
            info_dict["csar_metadata"] = csar_meta.to_dict()
        except OperaError:
            # anything that fails because of validation can be ignored, we can use state
            # we mark the CSAR as invalid because it's useful to know
            pass

    # detection from state, overrides stateless
    if storage.exists("root_file"):
        service_template = storage.read("root_file")
        info_dict["service_template"] = service_template

        if storage.exists("inputs"):
            inputs = yaml.safe_load(storage.read("inputs"))
        else:
            inputs = {}
        info_dict["inputs"] = inputs

        if storage.exists("csars/csar"):
            csar_dir = Path(storage.path) / "csars" / "csar"
            info_dict["content_root"] = str(csar_dir)
            ast = tosca.load(Path(csar_dir), PurePath(service_template).relative_to(csar_dir))
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
