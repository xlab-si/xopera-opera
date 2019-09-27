from opera.csar import ToscaCsar
from opera.error import ParseError
from opera.parser.parser import ToscaParser


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "validate",
        help="Validate service template"
    )
    parser.add_argument("csar",
                        help="TOSCA CSAR directory or .zip file")
    parser.set_defaults(func=validate)


def validate(args):
    print("Validating service template ...")
    try:
        csar = ToscaCsar.load(args.csar)
        parsed = ToscaParser.parse(csar)
        print(parsed)
        print("Done.")
        return 0
    except ParseError as e:
        print("%s: %s", e.loc, e)
        return 1
