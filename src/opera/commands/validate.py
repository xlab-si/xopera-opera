from opera.csar import ToscaCsar
from opera.error import ParseError
from opera.log import get_logger
from opera.parser.parser import ToscaParser

logger = get_logger()


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "validate",
        help="Validate service template"
    )
    parser.add_argument("csar",
                        help="TOSCA CSAR directory or .zip file")
    parser.set_defaults(func=validate)


def validate(args):
    logger.info("Validating service template ...")
    try:
        csar = ToscaCsar.load(args.csar)
        parsed = ToscaParser.parse(csar)
        logger.info(parsed)
        logger.info("Done.")
        return 0
    except ParseError as e:
        logger.error("%s: %s", e.loc, e)
        return 1
