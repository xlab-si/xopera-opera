import argparse
import typing
from pathlib import Path, PurePath
from zipfile import is_zipfile

import shtab
import yaml
from opera_tosca_parser.commands.parse import parse_service_template, parse_csar

from opera.error import OperaError, ParseError
from opera.storage import Storage
from opera.instance.topology import Topology


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "validate",
        help="Validate TOSCA service template or CSAR"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help="Storage folder location (instead of default .opera)"
    )
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="YAML or JSON file with inputs",
    ).complete = shtab.FILE
    parser.add_argument(
        "--executors", "-e", action="store_true",
        help="Validate TOSCA templates and also the executors (e.g., Ansible playbooks) behind them",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Turns on verbose mode",
    )
    parser.add_argument(
        "csar_or_service_template", type=str, nargs="?",
        help="TOSCA YAML service template file or CSAR"
    ).complete = shtab.FILE
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    try:
        inputs = yaml.safe_load(args.inputs) if args.inputs else {}
    except yaml.YAMLError as e:
        print(f"Invalid inputs: {e}")
        return 1

    storage = Storage.create(args.instance_path)

    if args.csar_or_service_template is None:
        csar_or_st_path = PurePath(".")
    else:
        csar_or_st_path = PurePath(args.csar_or_service_template)

    try:
        print("Validating TOSCA CSAR or service template...")
        validate(csar_or_st_path, inputs, storage, args.verbose, args.executors)
        print("Done.")
    except ParseError as e:
        print(f"{e.loc}: {e}")
        return 1
    except OperaError as e:
        print(str(e))
        return 1

    return 0


def validate(csar_or_st_path: PurePath, inputs: typing.Optional[dict], storage: Storage, verbose: bool,
             executors: bool):
    if is_zipfile(csar_or_st_path) or Path(csar_or_st_path).is_dir():
        validate_csar(csar_or_st_path, inputs, storage, verbose, executors)
    else:
        validate_service_template(csar_or_st_path, inputs, storage, verbose, executors)


def validate_csar(csar_path: PurePath, inputs: typing.Optional[dict], storage: Storage, verbose: bool,
                  executors: bool):
    if inputs is None:
        inputs = {}

    template, workdir = parse_csar(csar_path, inputs)
    if executors:
        topology = Topology.instantiate(template, storage)
        topology.validate(verbose, workdir, 1)


def validate_service_template(service_template_path: PurePath, inputs: typing.Optional[dict], storage: Storage,
                              verbose: bool, executors: bool):
    if inputs is None:
        inputs = {}

    template, workdir = parse_service_template(service_template_path, inputs)
    if executors:
        topology = Topology.instantiate(template, storage)
        topology.validate(verbose, workdir, 1)
