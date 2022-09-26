import argparse
import typing
from os import path
from pathlib import Path, PurePath
from zipfile import ZipFile, is_zipfile

import shtab
import yaml
from opera_tosca_parser.commands.parse import parse_csar, parse_service_template
from opera_tosca_parser.parser import tosca

from opera.commands.info import info
from opera.error import DataError, ParseError
from opera.instance.topology import Topology
from opera.storage import Storage
from opera.utils import prompt_yes_no_question


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "deploy",
        help="Deploy TOSCA service template or CSAR"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help="Storage folder location (instead of default .opera)"
    )
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="YAML or JSON file with inputs to override the inputs supplied in init",
    ).complete = shtab.FILE
    parser.add_argument(
        "--workers", "-w", type=int, default=1,
        help="Maximum number of concurrent deployment threads (positive number, default 1)"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--resume", "-r", action="store_true",
        help="Resume the deployment from where it was interrupted",
    )
    group.add_argument(
        "--clean-state", "-c", action="store_true",
        help="Clean the previous deployment state and start over the deployment",
    )

    parser.add_argument(
        "--force", "-f", action="store_true",
        help="Force the action and skip any possible prompts",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Turns on verbose mode",
    )
    parser.add_argument(
        "template", type=argparse.FileType("r"), nargs="?",
        help="TOSCA YAML service template file or CSAR",
    ).complete = shtab.FILE
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):  # pylint: disable=too-many-statements
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError(f"Directory {args.instance_path} is not a valid path!")

    if args.workers < 1:
        print(f"{args.workers} is not a positive number!")
        return 1

    storage = Storage.create(args.instance_path)
    status = info(None, storage)["status"]
    delete_existing_state = False

    if storage.exists("instances"):
        if args.resume and status == "error":
            if not args.force:
                print("The resume deploy option might have unexpected consequences on the already deployed blueprint.")
                question = prompt_yes_no_question()
                if not question:
                    return 0
        elif args.clean_state:
            if args.force:
                delete_existing_state = True
            else:
                print("The clean state deploy option might have unexpected "
                      "consequences on the already deployed blueprint.")
                question = prompt_yes_no_question()
                if question:
                    delete_existing_state = True
                else:
                    return 0
        elif status == "initialized":
            print("The project is initialized. You have to deploy it first to be able to run undeploy.")
            return 0
        elif status == "undeploying":
            print("The project is currently undeploying. Please try again after the undeployment.")
            return 0
        elif status == "deployed":
            print("All instances have already been deployed.")
            return 0
        elif status == "error":
            print("The instance model already exists. Use --resume/-r to continue or --clean-state/-c to delete "
                  "current deployment state and start over the deployment.")
            return 0

    if args.template:
        csar_or_st_path = PurePath(args.template.name)
    else:
        if storage.exists("root_file"):
            csar_or_st_path = PurePath(storage.read("root_file"))
        else:
            print("CSAR or template root file does not exist. Maybe you have forgotten to initialize it.")
            return 1

    try:
        if args.inputs:
            inputs = yaml.safe_load(args.inputs)
        else:
            inputs = None
    except yaml.YAMLError as e:
        print(f"Invalid inputs: {e}")
        return 1

    try:
        if is_zipfile(csar_or_st_path):
            deploy_compressed_csar(csar_or_st_path, inputs, storage,
                                   args.verbose, args.workers,
                                   delete_existing_state)
        else:
            deploy_service_template(csar_or_st_path, inputs, storage,
                                    args.verbose, args.workers,
                                    delete_existing_state)
    except ParseError as e:
        print(f"{e.loc}: {e}")
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def deploy_service_template(
        service_template_path: PurePath,
        inputs: typing.Optional[dict],
        storage: Storage,
        verbose_mode: bool,
        num_workers: int,
        delete_existing_state: bool
):
    if delete_existing_state:
        storage.remove("instances")

    if inputs is None:
        if storage.exists("inputs"):
            inputs = yaml.safe_load(storage.read("inputs"))
        else:
            inputs = {}
    storage.write_json(inputs, "inputs")
    storage.write(str(service_template_path), "root_file")

    # initialize service template and deploy
    template, workdir = parse_service_template(service_template_path, inputs)
    topology = Topology.instantiate(template, storage)
    topology.deploy(verbose_mode, workdir, num_workers)


def deploy_compressed_csar(
        csar_path: PurePath,
        inputs: typing.Optional[dict],
        storage: Storage,
        verbose_mode: bool,
        num_workers: int,
        delete_existing_state: bool
):
    if delete_existing_state:
        storage.remove("instances")

    if inputs is None:
        inputs = {}
    storage.write_json(inputs, "inputs")

    csars_dir = Path(storage.path) / "csars"
    csars_dir.mkdir(exist_ok=True)

    csar = tosca.load_csar(csar_path)
    tosca_service_template = csar.get_entrypoint()

    # unzip csar, save the path to storage and set workdir
    csar_dir = csars_dir / Path("csar")
    ZipFile(csar_path, "r").extractall(csar_dir)  # pylint: disable=consider-using-with
    csar_tosca_service_template_path = csar_dir / tosca_service_template
    storage.write(str(csar_tosca_service_template_path), "root_file")
    workdir = str(csar_dir)
    template, _ = parse_csar(csar_path, inputs)
    topology = Topology.instantiate(template, storage)
    topology.deploy(verbose_mode, workdir, num_workers)
