import argparse
from pathlib import Path, PurePath

from opera.error import ParseError
from opera.log import get_logger
from opera.parser import tosca

logger = get_logger()


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "validate",
        help="Validate service template"
    )
    parser.add_argument("template",
                        type=argparse.FileType("r"),
                        help="Service template root")
    parser.set_defaults(func=validate)


def validate(args):
    logger.info("Validating service template ...")
    try:
        logger.info(tosca.load(Path.cwd(), PurePath(args.template.name)))
        logger.info("Done.")
        return 0
    except ParseError as e:
        logger.error("{}: {}".format(e.loc, e))
        return 1
