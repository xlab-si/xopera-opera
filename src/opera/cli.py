import argparse
import inspect
import sys

import pkg_resources
import shtab

from opera import commands


class ArgParser(argparse.ArgumentParser):
    """An argument parser that displays help on error."""

    def error(self, message):
        sys.stderr.write(f"error: {message}\n")
        self.print_help()
        sys.exit(2)

    def add_subparsers(self, **kwargs):
        # Workaround for http://bugs.python.org/issue9253
        subparsers = super(ArgParser, self).add_subparsers()  # pylint: disable=super-with-arguments
        subparsers.required = True
        subparsers.dest = "command"
        return subparsers


class PrintCurrentVersionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            print(pkg_resources.get_distribution("opera").version)
            parser.exit(0)
        except pkg_resources.DistributionNotFound as e:
            print(f"Error when retrieving current opera version: {e}")
            parser.exit(1)


def create_parser():
    parser = ArgParser(
        description="opera orchestrator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    subparsers = parser.add_subparsers()
    cmds = inspect.getmembers(commands, inspect.ismodule)
    for _, module in sorted(cmds, key=lambda x: x[0]):
        module.add_parser(subparsers)
    return parser


def main():
    parser = create_parser()
    # use shtab magic
    # add global optional argument for generating shell completion script
    shtab.add_argument_to(
        parser, ["-s", "--shell-completion"],
        help="Generate tab completion script for your shell"
    )
    parser.add_argument(
        "--version", "-v", action=PrintCurrentVersionAction, nargs=0, help="Get current opera package version"
    )
    args = parser.parse_args()
    return args.func(args)
