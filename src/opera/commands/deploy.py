import argparse
import typing
from os import chdir, path
from pathlib import Path, PurePath

import yaml

from opera.utils import prompt_yes_no_question
from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "deploy",
        help="Deploy service template from CSAR"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help=".opera storage folder location"
    )
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="Optional: YAML file with inputs to "
             "override the inputs supplied in init",
    )
    parser.add_argument(
        "--workers", "-w",
        help="Maximum number of concurrent deployment "
             "threads (positive number, default 1)",
        type=int, default=1
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--resume", "-r", action='store_true',
        help="Resume the deployment from where it was interrupted",
    )
    group.add_argument(
        "--clean-state", "-c", action='store_true',
        help="Clean the previous deployment state "
             "and start over the deployment",
    )
    parser.add_argument(
        "--force", "-f", action='store_true',
        help="Force the action and skip any possible prompts",
    )
    parser.add_argument(
        "--verbose", "-v", action='store_true',
        help="Turns on verbose mode",
    )
    parser.add_argument("template",
                        type=argparse.FileType("r"), nargs='?',
                        help="TOSCA YAML service template file",
                        )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {0} is not a valid path!"
                                         .format(args.instance_path))

    storage = Storage.create(args.instance_path)

    if args.workers < 1:
        print("{0} is not a positive number!".format(args.workers))
        return 1

    delete_existing_state = False
    if storage.exists("instances"):
        if args.resume:
            if not args.force:
                print("The resume deploy option might have unexpected "
                      "consequences on the already deployed blueprint.")
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
        else:
            print("The instance model already exists. Use --resume to "
                  "continue or --clean-state to delete current deployment "
                  "state and start over the deployment.")
            return 0

    if args.template:
        service_template = args.template.name
    else:
        if storage.exists("root_file"):
            service_template = storage.read("root_file")
        else:
            print("CSAR or template root file does not exist. "
                  "Maybe you have forgotten to initialize it.")
            return 1

    try:
        if args.inputs:
            inputs = yaml.safe_load(args.inputs)
        else:
            inputs = None
    except Exception as e:
        print("Invalid inputs: {}".format(e))
        return 1

    try:
        deploy(service_template, inputs, storage, args.verbose, args.workers,
               delete_existing_state)
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def deploy(service_template: str, inputs: typing.Optional[dict],
           storage: Storage, verbose_mode: bool, num_workers: int,
           delete_existing_state: bool):
    """
    :raises ParseError:
    :raises DataError:
    """
    if delete_existing_state:
        storage.remove("instances")

    if inputs is None:
        if storage.exists("inputs"):
            inputs = yaml.safe_load(storage.read("inputs"))
        else:
            inputs = {}
    storage.write_json(inputs, "inputs")
    storage.write(service_template, "root_file")

    if storage.exists("csars"):
        csar_dir = Path(storage.path) / "csars" / "csar"
        ast = tosca.load(Path(csar_dir),
                         PurePath(service_template).relative_to(csar_dir))
        chdir(csar_dir)
    else:
        ast = tosca.load(Path.cwd(), PurePath(service_template))

    template = ast.get_template(inputs)
    topology = template.instantiate(storage)
    topology.deploy(verbose_mode, num_workers)
