import argparse
from pathlib import Path, PurePath

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "undeploy",
        help="Undeploy service template"
    )
    parser.set_defaults(func=undeploy)


def undeploy(args):
    storage = Storage(Path(".opera"))
    root = storage.read("root_file")
    inputs = storage.read_json("inputs")

    try:
        ast = tosca.load(Path.cwd(), PurePath(root))
        template = ast.get_template(inputs)
        topology = template.instantiate(storage)
        topology.undeploy()
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0
