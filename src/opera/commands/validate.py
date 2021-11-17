import argparse
import typing
from pathlib import Path, PurePath
from tempfile import TemporaryDirectory
from zipfile import is_zipfile

import shtab
import yaml

from opera.error import OperaError, ParseError
from opera.parser import tosca
from opera.parser.tosca.csar import CloudServiceArchive, DirCloudServiceArchive
from opera.storage import Storage


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
        if is_zipfile(csar_or_st_path) or Path(csar_or_st_path).is_dir():
            print("Validating CSAR...")
            validate_csar(csar_or_st_path, inputs, storage, args.verbose, args.executors)
        else:
            print("Validating service template...")
            validate_service_template(csar_or_st_path, inputs, storage, args.verbose, args.executors)
        print("Done.")
    except ParseError as e:
        print(f"{e.loc}: {e}")
        return 1
    except OperaError as e:
        print(str(e))
        return 1

    return 0


def validate_csar(csar_path: PurePath, inputs: typing.Optional[dict], storage: Storage, verbose: bool,
                  executors: bool):
    if inputs is None:
        inputs = {}

    csar = CloudServiceArchive.create(csar_path)
    csar.validate_csar()
    entrypoint = csar.get_entrypoint()

    if entrypoint is not None:
        if isinstance(csar, DirCloudServiceArchive):
            workdir = Path(csar_path)
            ast = tosca.load(workdir, entrypoint)
            template = ast.get_template(inputs)
            if executors:
                topology = template.instantiate(storage)
                topology.validate(verbose, workdir, 1)
        else:
            with TemporaryDirectory() as csar_validation_dir:
                csar.unpackage_csar(csar_validation_dir)
                workdir = Path(csar_validation_dir)
                ast = tosca.load(workdir, entrypoint)
                template = ast.get_template(inputs)
                if executors:
                    topology = template.instantiate(storage)
                    topology.validate(verbose, csar_validation_dir, 1)


def validate_service_template(service_template_path: PurePath, inputs: typing.Optional[dict], storage: Storage,
                              verbose: bool, executors: bool):
    if inputs is None:
        inputs = {}
    workdir = Path(service_template_path.parent)
    ast = tosca.load(workdir, PurePath(service_template_path.name))
    template = ast.get_template(inputs)
    if executors:
        topology = template.instantiate(storage)
        topology.validate(verbose, workdir, 1)
