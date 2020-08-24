import argparse
import typing
from os import path
from pathlib import Path, PurePath
from zipfile import ZipFile, is_zipfile

import yaml

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.parser.tosca.csar import CloudServiceArchive
from opera.storage import Storage


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "init",
        help="Initialize the deployment environment "
             "for the service template or CSAR"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help=".opera storage folder location"
    )
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="YAML file with inputs",
    )
    parser.add_argument(
        "--verbose", "-v", action='store_true',
        help="Turns on verbose mode",
    )
    parser.add_argument("csar",
                        type=argparse.FileType("r"),
                        help="Cloud service archive or service template file")
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {0} is not a valid path!"
                                         .format(args.instance_path))

    storage = Storage.create(args.instance_path)

    try:
        inputs = yaml.safe_load(args.inputs) if args.inputs else {}
    except Exception as e:
        print("Invalid inputs: {}".format(e))
        return 1

    try:
        if is_zipfile(args.csar.name):
            initialize_compressed_csar(args.csar.name, inputs, storage)
            print("CSAR was initialized")
        else:
            initialize_service_template(args.csar.name, inputs, storage)
            print("Service template was initialized")
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1
    except Exception as e:
        print("Invalid CSAR: {}".format(e))
        return 1

    return 0


def initialize_compressed_csar(csar_name: str,
                               inputs: typing.Optional[dict],
                               storage: Storage):
    if inputs is None:
        inputs = {}
    storage.write_json(inputs, "inputs")

    csars_dir = Path(storage.path) / "csars"
    csars_dir.mkdir(exist_ok=True)

    # validate csar
    csar = CloudServiceArchive(csar_name, csars_dir)
    tosca_service_template = csar.validate_csar()

    # unzip csar and save the path to storage
    csar_dir = csars_dir / Path("csar")
    ZipFile(csar_name, 'r').extractall(csar_dir)
    csar_tosca_service_template_path = csar_dir / tosca_service_template
    storage.write(str(csar_tosca_service_template_path), "root_file")

    # try to initiate service template from csar
    ast = tosca.load(Path.cwd(), csar_tosca_service_template_path)
    template = ast.get_template(inputs)
    template.instantiate(storage)


def initialize_service_template(service_template: str,
                                inputs: typing.Optional[dict],
                                storage: Storage):
    if inputs is None:
        inputs = {}
    storage.write_json(inputs, "inputs")
    storage.write(service_template, "root_file")

    ast = tosca.load(Path.cwd(), PurePath(service_template))
    template = ast.get_template(inputs)
    template.instantiate(storage)
