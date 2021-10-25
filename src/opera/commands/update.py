import argparse
import tempfile
from os import path
from pathlib import Path

import shtab
import yaml

from opera.commands.diff import diff_instances
from opera.compare.diff import Diff
from opera.compare.instance_comparer import InstanceComparer
from opera.compare.template_comparer import TemplateComparer
from opera.error import DataError, ParseError
from opera.storage import Storage
from opera.utils import format_outputs, get_template, get_workdir


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "update",
        help="Update the deployed TOSCA service template and redeploy it according to the discovered template diff"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help="Storage folder location (instead of default .opera)"
    ).complete = shtab.DIR
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="Optional: YAML or JSON file with inputs that will be used for deployment update",
    ).complete = shtab.FILE
    parser.add_argument(
        "--workers", "-w", type=int, default=1,
        help="Maximum number of concurrent update threads (positive number, default 1)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Turns on verbose mode",
    )
    parser.add_argument(
        "template", type=argparse.FileType("r"), nargs="?",
        help="TOSCA YAML service template file",
    ).complete = shtab.FILE
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError(f"Directory {args.instance_path} is not a valid path!")

    if args.workers < 1:
        print(f"{args.workers} is not a positive number!")
        return 1

    storage_old = Storage.create(args.instance_path)
    comparer = TemplateComparer()
    instance_comparer = InstanceComparer()

    if args.template:
        service_template_new = args.template.name
    else:
        print("Template file for update was not supplied.")
        return 1

    try:
        if args.inputs:
            inputs_new = yaml.safe_load(args.inputs)
        else:
            inputs_new = {}
    except yaml.YAMLError as e:
        print(f"Invalid inputs: {e}")
        return 1

    workdir_old = get_workdir(storage_old)

    try:
        with tempfile.TemporaryDirectory() as temp_path:
            storage_new = Storage.create(temp_path)
            storage_new.write_json(inputs_new, "inputs")
            storage_new.write(service_template_new, "root_file")
            workdir_new = get_workdir(storage_new)

            instance_diff = diff_instances(
                storage_old, workdir_old,
                storage_new, workdir_new,
                comparer,
                instance_comparer,
                args.verbose
            )

            update(
                storage_old, workdir_old,
                storage_new, workdir_new,
                instance_comparer,
                instance_diff,
                args.verbose,
                args.workers,
                overwrite=True
            )

    except ParseError as e:
        print(f"{e.loc}: {e}")
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def update(
        storage_old: Storage, workdir_old: Path,
        storage_new: Storage, workdir_new: Path,
        instance_comparer: InstanceComparer,
        instance_diff: Diff,
        verbose_mode: bool,
        num_workers: int,
        overwrite: bool
):
    template_old = get_template(storage_old, workdir_old)
    template_new = get_template(storage_new, workdir_new)
    topology_old = template_old.instantiate(storage_old)
    topology_new = template_new.instantiate(storage_new)

    if verbose_mode:
        print(format_outputs(instance_diff.outputs(), "json"))

    instance_comparer.prepare_update(topology_old, topology_new, instance_diff)
    topology_old.undeploy(verbose_mode, workdir_old, num_workers)
    topology_old.write_all()

    if overwrite:
        # swap storage
        topology_new.set_storage(storage_old)
        # rewrite inputs and root file
        storage_old.write_json(storage_new.read_json("inputs"), "inputs")
        storage_old.write(storage_new.read("root_file"), "root_file")

    topology_new.write_all()
    topology_new.deploy(verbose_mode, workdir_new, num_workers)
