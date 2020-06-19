import argparse
from os import path
from pathlib import Path, PurePath
from zipfile import ZipFile, is_zipfile

import yaml

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage
from opera.parser.tosca.csar import CloudServiceArchive


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "init",
        help="Initialize the deployment environment for the service template or CSAR"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help=".opera storage folder location"
    )
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="YAML file with inputs",
    )
    parser.add_argument("csar",
                        type=argparse.FileType("r"),
                        help="Cloud service archive or service template file")
    parser.set_defaults(func=init)


def init(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {0} is not a valid path!".format(args.instance_path))

    storage = Storage(Path(args.instance_path)) if args.instance_path else Storage(Path(".opera"))

    if is_zipfile(args.csar.name):
        initialize_compressed_csar(args, storage)
    else:
        storage.write(args.csar.name, "root_file")
        initialize_service_template(args, storage)


def initialize_service_template(args, storage):
    try:
        inputs = yaml.safe_load(args.inputs) if args.inputs else {}
        storage.write_json(inputs, "inputs")
    except Exception as e:
        print("Invalid inputs: {}".format(e))
        return 1

    try:
        ast = tosca.load(Path.cwd(), PurePath(args.csar.name))
        template = ast.get_template(inputs)
        template.instantiate(storage)
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    print("Service template was initialized")
    return 0


def initialize_compressed_csar(args, storage):
    csars_dir = Path(storage.path) / "csars"
    csars_dir.mkdir(exist_ok=True)
    csar_name = args.csar.name

    try:
        inputs = yaml.safe_load(args.inputs) if args.inputs else {}
        storage.write_json(inputs, "inputs")
    except Exception as e:
        print("Invalid inputs: {}".format(e))
        return 1

    try:
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
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1
    except Exception as e:
        print("Invalid CSAR: {}".format(e))
        return 1

    print("CSAR was initialized")
    return 0
