from __future__ import print_function, unicode_literals

import argparse
import pkg_resources
import sys

import yaml

from opera import types


class ArgParser(argparse.ArgumentParser):
    """
    Argument parser that displays help on error
    """

    def error(self, message):
        sys.stderr.write("error: {}\n".format(message))
        self.print_help()
        sys.exit(2)

    def add_subparsers(self):
        # Workaround for http://bugs.python.org/issue9253
        subparsers = super(ArgParser, self).add_subparsers()
        subparsers.required = True
        subparsers.dest = "command"
        return subparsers


def create_parser():
    parser = ArgParser(description="opera orchestrator",
                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers()
    create_deploy_parser(subparsers)
    return parser


def create_deploy_parser(subparsers):
    parser = subparsers.add_parser("deploy", help="Deploy service template")
    parser.add_argument("template", type=argparse.FileType("r"),
                        help="service template yaml file")


def load_standard_library():
    return yaml.safe_load(
        pkg_resources.resource_stream(__name__, "types.yaml"),
    )


def main():
    parser = create_parser()
    args = parser.parse_args()

    service_template = types.ServiceTemplate.from_data(
        load_standard_library(), []
    )
    service_template.merge(types.ServiceTemplate.from_data(
        yaml.safe_load(args.template), []
    ))
    service_template.resolve()
    instances = service_template.instantiate(None)

    for i in instances:
        i.deploy()

    return 0
