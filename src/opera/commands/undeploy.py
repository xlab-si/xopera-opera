import argparse
from os import path
from pathlib import PurePath

import shtab
from opera_tosca_parser.commands.parse import parse_service_template

from opera.commands.info import info
from opera.error import DataError, ParseError
from opera.storage import Storage
from opera.utils import prompt_yes_no_question
from opera.instance.topology import Topology


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "undeploy",
        help="Undeploy TOSCA service template or CSAR"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help="Storage folder location (instead of default .opera)"
    ).complete = shtab.DIR
    parser.add_argument(
        "--workers", "-w", type=int, default=1,
        help="Maximum number of concurrent undeployment threads (positive number, default 1)"
    )
    parser.add_argument(
        "--resume", "-r", action="store_true",
        help="Resume the undeployment from where it was interrupted",
    )
    parser.add_argument(
        "--force", "-f", action="store_true",
        help="Force the action and skip any possible prompts",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Turns on verbose mode",
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError(f"Directory {args.instance_path} is not a valid path!")

    if args.workers < 1:
        print(f"{args.workers} is not a positive number!")
        return 1

    storage = Storage.create(args.instance_path)
    status = info(None, storage)["status"]

    if storage.exists("instances"):
        if args.resume and status == "error":
            if not args.force:
                print("The resume undeploy option might have unexpected consequences on the already "
                      "undeployed blueprint.")
                question = prompt_yes_no_question()
                if not question:
                    return 0
        elif status == "initialized":
            print("The project is initialized. You have to deploy it first to be able to run undeploy.")
            return 0
        elif status == "deploying":
            print("The project is currently deploying. Please try again after the deployment.")
            return 0
        elif status == "undeployed":
            print("All instances have already been undeployed.")
            return 0
        elif status == "error":
            print("The instance model already exists. Use --resume/-r option to continue current undeployment process.")
            return 0

    try:
        undeploy(storage, args.verbose, args.workers)
    except ParseError as e:
        print(f"{e.loc}: {e}")
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def undeploy(storage: Storage, verbose_mode: bool, num_workers: int):
    """
    Undeploy a deployment.

    :raises ParseError:
    :raises DataError:
    """
    if storage.exists("inputs"):
        inputs = storage.read_json("inputs")
    else:
        inputs = {}

    if storage.exists("root_file"):
        service_template_path = PurePath(storage.read("root_file"))

        template, workdir = parse_service_template(service_template_path, inputs)
        topology = Topology.instantiate(template, storage)
        topology.undeploy(verbose_mode, workdir, num_workers)
    else:
        print("There is no root_file in storage.")
