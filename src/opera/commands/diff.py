import argparse
import typing
import yaml
import tempfile

from pathlib import Path, PurePath
from os import path

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage
from opera.compare.template_comparer import TemplateComparer, TemplateContext
from opera.compare.instance_comparer import InstanceComparer
from opera.utils import format_outputs, save_outputs, get_template, get_workdir


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "diff",
        help="Compare TOSCA service template to the one from "
             "the opera project storage and print out their differences"
    )
    parser.add_argument(
        "--instance-path", "-p",
        help=".opera storage folder location"
    )
    parser.add_argument(
        "--inputs", "-i", type=argparse.FileType("r"),
        help="Optional: YAML or JSON file with inputs "
             "that will be used along with the comparison",
    )
    parser.add_argument(
        "--verbose", "-v", action='store_true',
        help="Turns on verbose mode",
    )
    parser.add_argument(
        "--template-only", "-t", action='store_true',
        help="Compare only templates without instances",
    )
    parser.add_argument(
        "--format", "-f", choices=("yaml", "json"), type=str,
        default="yaml", help="Output format",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file location"
    )
    parser.add_argument("template",
                        type=argparse.FileType("r"), nargs='?',
                        help="TOSCA YAML service template file",
                        )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args):
    if args.instance_path and not path.isdir(args.instance_path):
        raise argparse.ArgumentTypeError("Directory {} is not a valid path!"
                                         .format(args.instance_path))

    storage_old = Storage.create(args.instance_path)
    comparer = TemplateComparer()

    if args.template:
        service_template_new = args.template.name
    else:
        print("Template file for comparison was not supplied.")
        return 1

    if storage_old.exists("root_file"):
        service_template_old = storage_old.read("root_file")
    else:
        print("There is no root_file in storage.")
        return 1

    if storage_old.exists("inputs"):
        inputs_old = storage_old.read_json("inputs")
    else:
        inputs_old = {}

    try:
        if args.inputs:
            inputs_new = yaml.safe_load(args.inputs)
        else:
            inputs_new = {}
    except Exception as e:
        print("Invalid inputs: {}".format(e))
        return 1

    workdir_old = get_workdir(storage_old)
    workdir_new = str(Path.cwd())

    try:
        if args.template_only:
            template_diff = diff_templates(service_template_old,
                                           workdir_old, inputs_old,
                                           service_template_new,
                                           workdir_new, inputs_new,
                                           comparer, args.verbose)
        else:
            instance_comparer = InstanceComparer()
            with tempfile.TemporaryDirectory() as temp_path:
                storage_new = Storage.create(temp_path)
                storage_new.write_json(inputs_new, "inputs")
                storage_new.write(service_template_new, "root_file")
                template_diff = diff_instances(storage_old, workdir_old,
                                               storage_new, workdir_new,
                                               comparer,
                                               instance_comparer, args.verbose)
        outputs = template_diff.outputs()
        if args.output:
            save_outputs(outputs, args.format, args.output)
        else:
            print(format_outputs(outputs, args.format))
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0


def diff_templates(service_template_old: str, workdir_old: str,
                   inputs_old: typing.Optional[dict],
                   service_template_new: str, workdir_new: str,
                   inputs_new: typing.Optional[dict],
                   template_comparer: TemplateComparer, verbose_mode: bool):
    """
    :raises ParseError:
    :raises DataError:
    """
    if inputs_new is None:
        inputs_new = {}

    if inputs_old is None:
        inputs_old = {}

    ast_old = tosca.load(Path(workdir_old), PurePath(service_template_old))
    ast_new = tosca.load(Path(workdir_new), PurePath(service_template_new))

    template_old = ast_old.get_template(inputs_old)
    template_new = ast_new.get_template(inputs_new)
    context = TemplateContext(template_old,
                              template_new,
                              workdir_old,
                              workdir_new)

    equal, diff = template_comparer.compare_service_template(template_old,
                                                             template_new,
                                                             context)
    return diff


def diff_instances(storage_old: Storage, workdir_old: str,
                   storage_new: Storage, workdir_new: str,
                   template_comparer: TemplateComparer,
                   instance_comparer: InstanceComparer,
                   verbose_mode: bool):
    """
    :raises ParseError:
    :raises DataError:
    """

    template_old = get_template(storage_old)
    template_new = get_template(storage_new)
    topology_old = template_old.instantiate(storage_old)
    topology_new = template_new.instantiate(storage_new)

    context = TemplateContext(template_old,
                              template_new,
                              workdir_old,
                              workdir_new)

    equal, diff = template_comparer.compare_service_template(template_old,
                                                             template_new,
                                                             context)

    equal, diff = instance_comparer.compare_topology_template(topology_old,
                                                              topology_new,
                                                              diff)

    return diff
