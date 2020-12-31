import argparse
import shtab

from pathlib import Path, PurePath
from os import path

from opera.commands.info import info
from opera.utils import prompt_yes_no_question
from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "undeploy",
        help="Undeploy service template"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help=".opera storage folder location"
    ).complete = shtab.DIR
    parser.add_argument(
        "--workers", "-w",
        help="Maximum number of concurrent undeployment "
             "threads (positive number, default 1)",
        type=int, default=1
    )
    parser.add_argument(
        "--resume", "-r", action='store_true',
        help="Resume the undeployment from where it was interrupted",
    )
    parser.add_argument(
        "--force", "-f", action='store_true',
        help="Force the action and skip any possible prompts",
    )
    parser.add_argument(
        "--verbose", "-v", action='store_true',
        help="Turns on verbose mode",
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {} is not a valid path!"
                                         .format(args.instance_path))

    if args.workers < 1:
        print("{} is not a positive number!".format(args.workers))
        return 1

    storage = Storage.create(args.instance_path)
    status = info(None, storage)["status"]

    if storage.exists("instances"):
        if args.resume and status == "interrupted":
            if not args.force:
                print("The resume undeploy option might have unexpected "
                      "consequences on the already undeployed blueprint.")
                question = prompt_yes_no_question()
                if not question:
                    return 0
        elif status == "interrupted":
            print("The instance model already exists. Use --resume/-r option "
                  "to continue current undeployment process.")
            return 0
        elif status == "undeployed":
            print("All instances have already been undeployed.")
            return 0

    try:
        undeploy(storage, args.verbose, args.workers)
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def undeploy(storage: Storage, verbose_mode: bool, num_workers: int):
    """
    :raises ParseError:
    :raises DataError:
    """
    if storage.exists("inputs"):
        inputs = storage.read_json("inputs")
    else:
        inputs = {}

    if storage.exists("root_file"):
        service_template = storage.read("root_file")
        workdir = str(Path.cwd())

        if storage.exists("csars"):
            csar_dir = Path(storage.path) / "csars" / "csar"
            workdir = str(csar_dir)
            ast = tosca.load(Path(csar_dir),
                             PurePath(service_template).relative_to(csar_dir))
        else:
            ast = tosca.load(Path.cwd(), PurePath(service_template))

        template = ast.get_template(inputs)
        topology = template.instantiate(storage)
        topology.undeploy(verbose_mode, workdir, num_workers)
    else:
        print("There is no root_file in storage.")
        return 0
