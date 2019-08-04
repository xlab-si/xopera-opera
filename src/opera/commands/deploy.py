import argparse

import yaml

from opera import csar, stdlib, types


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

    print("Loading service template ...")
    service_template = types.ServiceTemplate.from_data(stdlib.load())
    service_template.merge(
        types.ServiceTemplate.from_data(yaml.safe_load(args.csar))
    )

    print("Resolving service template links ...")
    service_template.resolve()

    print("Creating instance model ...")
    instances = service_template.instantiate()

    print("Deploying instance model ...")
    instances.deploy()

    print("Done.")

    return 0
