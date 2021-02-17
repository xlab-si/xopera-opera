import argparse
import typing
from os import path
from pathlib import Path, PurePath

import shtab
import yaml

from opera.commands.info import info
from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage
from opera.utils import prompt_yes_no_question


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "notify",
        help="Notify the orchestrator about changes after deployment and run triggers defined in TOSCA policies"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help="Storage folder location (instead of default .opera)"
    )
    parser.add_argument(
        "--trigger", "-t", "--event", "-e", metavar="TRIGGER_OR_EVENT", required=True,
        help="TOSCA policy trigger name or event that will invoke all the actions (interface operations) on policy",
    )
    parser.add_argument(
        "--notification", "-n", type=argparse.FileType("r"),
        help="Notification file (usually JSON) with changes that will be exposed to TOSCA interfaces",
    ).complete = shtab.FILE
    parser.add_argument(
        "--force", "-f", action="store_true",
        help="Skip any prompts and force execution",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose mode",
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {} is not a valid path!".format(args.instance_path))

    storage = Storage.create(args.instance_path)
    status = info(None, storage)["status"]

    if not args.force and storage.exists("instances"):
        if status == "initialized":
            print("Running notify without previously running deploy might have unexpected consequences.")
            question = prompt_yes_no_question()
            if not question:
                return 0
        if status == "interrupted":
            print("Running notify after an interrupted deployment might have unexpected consequences.")
            question = prompt_yes_no_question()
            if not question:
                return 0
        if status == "undeployed":
            print("Running notify in an undeployed project might have unexpected consequences.")
            question = prompt_yes_no_question()
            if not question:
                return 0

    if not args.force and not args.trigger:
        print("You have not specified which policy trigger to use (with --trigger/-t or --event/-e) "
              "and in this case all the triggers will be invoked which might not be what you want.")
        question = prompt_yes_no_question()
        if not question:
            return 0

    # read the notification file and the pass its contents to the library function
    notification_file_contents = Path(args.notification.name).read_text() if args.notification else None

    try:
        notify(storage, args.verbose, args.trigger, notification_file_contents)
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def notify(storage: Storage, verbose_mode: bool, trigger_name_or_event: str,
           notification_file_contents: typing.Optional[str]):
    if storage.exists("inputs"):
        inputs = yaml.safe_load(storage.read("inputs"))
    else:
        inputs = {}

    if storage.exists("root_file"):
        service_template = storage.read("root_file")
        workdir = str(Path.cwd())

        if storage.exists("csars"):
            csar_dir = Path(storage.path) / "csars" / "csar"
            workdir = str(csar_dir)
            ast = tosca.load(Path(csar_dir), PurePath(service_template).relative_to(csar_dir))
        else:
            ast = tosca.load(Path.cwd(), PurePath(service_template))

        template = ast.get_template(inputs)

        # check if specified trigger or event name exists in template
        if trigger_name_or_event:
            trigger_name_or_event_exists = False
            for policy in template.policies:
                for trigger in policy.triggers.values():
                    if trigger_name_or_event in (trigger.name, trigger.event.data):
                        trigger_name_or_event_exists = True
                        break

            if not trigger_name_or_event_exists:
                raise DataError("The provided trigger or event name does not exist: {}.".format(trigger_name_or_event))

        topology = template.instantiate(storage)
        topology.notify(verbose_mode, workdir, trigger_name_or_event, notification_file_contents)
    else:
        print("There is no root_file in storage.")
