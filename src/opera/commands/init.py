import argparse
import typing
from os import path
from pathlib import Path, PurePath
from zipfile import ZipFile, is_zipfile

import shtab
import yaml

from opera.error import DataError, ParseError, OperaError
from opera.parser import tosca
from opera.parser.tosca.csar import CloudServiceArchive
from opera.storage import Storage


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "init",
        help="Initialize the deployment environment for the TOSCA service template or CSAR"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help="Storage folder location (instead of default .opera)"
    ).complete = shtab.DIR
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="YAML or JSON file with inputs",
    ).complete = shtab.FILE
    parser.add_argument(
        "--clean", "-c", action="store_true",
        help="Clean storage by removing previously initialized TOSCA service template or CSAR",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Turns on verbose mode",
    )
    parser.add_argument(
        "csar", type=argparse.FileType("r"),
        help="TOSCA YAML service template file or CSAR"
    ).complete = shtab.FILE
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    print("Warning: 'opera init' command is deprecated and will probably be removed within one of the next releases. "
          "Please use 'opera deploy' to initialize and deploy service templates or compressed CSARs.")
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError(f"Directory {args.instance_path} is not a valid path!")

    storage = Storage.create(args.instance_path)
    try:
        inputs = yaml.safe_load(args.inputs) if args.inputs else {}
    except yaml.YAMLError as e:
        print(f"Invalid inputs: {e}")
        return 1

    try:
        if is_zipfile(args.csar.name):
            init_compressed_csar(PurePath(args.csar.name), inputs, storage, args.clean)
            print("CSAR was initialized")
        else:
            init_service_template(PurePath(args.csar.name), inputs, storage, args.clean)
            print("Service template was initialized")
    except ParseError as e:
        print(f"{e.loc}: {e}")
        return 1
    except DataError as e:
        print(str(e))
        return 1
    except OperaError as e:
        print(f"Invalid CSAR: {e}")
        return 1

    return 0


def init_compressed_csar(csar_path: PurePath, inputs: typing.Optional[dict], storage: Storage, clean_storage: bool):
    if storage.exists("root_file"):
        if clean_storage:
            storage.remove_all()
        else:
            print("Looks like service template or CSAR has already been initialized. "
                  "Use the --clean/-c flag to clear the storage.")
            return

    if inputs is None:
        inputs = {}
    storage.write_json(inputs, "inputs")

    csars_dir = Path(storage.path) / "csars"
    csars_dir.mkdir(exist_ok=True)

    csar = CloudServiceArchive.create(csar_path)
    csar.validate_csar()
    tosca_service_template = csar.get_entrypoint()

    # unzip csar and save the path to storage
    csar_dir = csars_dir / Path("csar")
    ZipFile(csar_path, "r").extractall(csar_dir)  # pylint: disable=consider-using-with
    csar_tosca_service_template_path = csar_dir / tosca_service_template
    storage.write(str(csar_tosca_service_template_path), "root_file")

    # try to initiate service template from csar
    ast = tosca.load(Path(csar_dir), Path(tosca_service_template))
    template = ast.get_template(inputs)
    template.instantiate(storage)


def init_service_template(service_template_path: PurePath, inputs: typing.Optional[dict], storage: Storage,
                          clean_storage: bool):
    if storage.exists("root_file"):
        if clean_storage:
            storage.remove_all()
        else:
            print("Looks like service template or CSAR has already been initialized. "
                  "Use --clean/-c flag to clear the storage.")
            return

    if inputs is None:
        inputs = {}
    storage.write_json(inputs, "inputs")
    storage.write(str(service_template_path), "root_file")

    ast = tosca.load(Path(service_template_path.parent), PurePath(service_template_path.name))
    template = ast.get_template(inputs)
    template.instantiate(storage)
