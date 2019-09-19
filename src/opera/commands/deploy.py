import argparse
from pathlib import Path, PurePath

from opera import csar
from opera.error import ParseError
from opera.parser import tosca


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "deploy",
        help="Deploy service template from CSAR"
    )
    parser.add_argument("name",
                        help="name of deployment to create")
    parser.add_argument("csar",
                        type=argparse.FileType("r"),
                        help="cloud service archive file")
    parser.set_defaults(func=deploy)


def deploy(args):
    csar.save(args.name, args.csar.name)
    status = 0

    print("Loading service template ...")
    try:
        ast = tosca.load(Path.cwd(), PurePath(args.csar.name))
        print("=======================")
        tmpl = template.build(ast)
        print(tmpl)
    except ParseError as e:
        print("{}: {}".format(e.loc, e))
        status = 1

    #    print("Resolving service template links ...")
    #    service_template.resolve()

    #    print("Creating instance model ...")
    #    instances = service_template.instantiate()

    #    print("Deploying instance model ...")
    #    instances.deploy()

    print("Done.")

    return status
