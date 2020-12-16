import argparse
import typing
import yaml
import json
from pathlib import Path, PurePath
from os import path

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage
from opera.compare.template_comparer import TemplateComparer, TemplateContext


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "diff",
        help="Compare service templates"
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
        "--verbose", "-v", action='store_true',
        help="Turns on verbose mode",
    )
    parser.add_argument(
        "--format", "-f", choices=("yaml", "json"), type=str,
        default="yaml", help="Output format",
    )
    parser.add_argument(
        "--output", "-o",
        help="output file location"
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

    storage = Storage.create(args.instance_path)
    comparer = TemplateComparer()

    if args.template:
        service_template_new = args.template.name
    else:
        print("Template file does not exist. ")
        return 1

    if storage.exists("root_file"):
        service_template_old = storage.read("root_file")
    else:
        print("There is no root_file in storage.")
        return 1

    if storage.exists("inputs"):
        inputs_old = storage.read_json("inputs")
    else:
        inputs_old = {}

    try:
        if args.inputs:
            inputs_new = yaml.safe_load(args.inputs)
        else:
            inputs_new = None
    except Exception as e:
        print("Invalid inputs: {}".format(e))
        return 1

    try:
        template_diff = diff(service_template_new, Path.cwd(), inputs_new,
                             service_template_old, Path.cwd(), inputs_old,
                             comparer, args.verbose)
        outputs = template_diff.outputs(2)
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


def format_outputs(outputs, format):
    if format == "json":
        return json.dumps(outputs, indent=2)
    if format == "yaml":
        return yaml.dump(outputs, default_flow_style=False)

    assert False, "BUG - invalid format"


def save_outputs(outputs, format, filename):
    with open(filename, 'w+') as outfile:
        if format == "json":
            return json.dumps(outputs, outfile, indent=2)
        if format == "yaml":
            return yaml.dump(outputs, outfile, default_flow_style=False)

        assert False, "BUG - invalid format"


def diff(service_template_new: str, workdir_new,
         inputs_new: typing.Optional[dict],
         service_template_old: str, workdir_old,
         inputs_old: typing.Optional[dict],
         comparer: TemplateComparer, verbose_mode: bool):
    """
    :raises ParseError:
    :raises DataError:
    """
    if inputs_new is None:
        inputs_new = {}

    if inputs_old is None:
        inputs_old = {}

    ast_old = tosca.load(workdir_old, PurePath(service_template_old))
    ast_new = tosca.load(workdir_new, PurePath(service_template_new))

    template_old = ast_old.get_template(inputs_old)
    template_new = ast_new.get_template(inputs_new)
    context = TemplateContext(template_old,
                              template_new,
                              workdir_old,
                              workdir_new)

    equal, diff = comparer.compare_service_template(template_old,
                                                    template_new, context)
    return diff
