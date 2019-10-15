import argparse
import pathlib

from opera.bundle import OperaBundle


def add_parser(subparsers):
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "init",
        help="Initialise the xOpera directory structure"
    )
    zip_or_link_group = parser.add_mutually_exclusive_group(required=True)
    zip_or_link_group.add_argument("--csar", help="Path to a TOSCA CSAR .zip file.")
    zip_or_link_group.add_argument("--link", help="Path to an exploded CSAR directory.")
    parser.set_defaults(func=initialise)


def initialise(args):
    print("Initialising xOpera in the current working directory.")

    base_dir = pathlib.Path.cwd() / OperaBundle.DIRECTORY_NAME
    if args.csar:
        csar_path = args.csar
    elif args.link:
        csar_path = args.link
    else:
        raise RuntimeError("Neither csar nor link were specified, this should never happen.")

    OperaBundle.init(base_dir, csar_path)
    print("xOpera directory structure initialised in {}".format(base_dir))
