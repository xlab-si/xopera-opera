import argparse
from pathlib import Path, PurePath

from opera.error import DataError, ParseError
from opera.parser import tosca
from opera.storage import Storage


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "deploy",
        help="Deploy service template from CSAR"
    )
    parser.add_argument("csar",
                        type=argparse.FileType("r"),
                        help="cloud service archive file")
    parser.set_defaults(func=deploy)


def deploy(args):
    storage = Storage(Path(".opera"))
    storage.write(args.csar.name, "root_file")

    try:
        ast = tosca.load(Path.cwd(), PurePath(args.csar.name))
        template = ast.get_template()
        topology = template.instantiate(storage)
        topology.deploy()
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        return 1
    except DataError as e:
        print(str(e))
        return 1

    return 0
