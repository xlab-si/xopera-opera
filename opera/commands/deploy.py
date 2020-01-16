import argparse

import yaml

from opera import csar, stdlib, types


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "deploy",
        help="Deploy service template from CSAR"
    )
    parser.add_argument("--inputs", "-i",
                        type=argparse.FileType("r"),
                        help="YAML file with inputs")
    parser.add_argument("name",
                        help="name of deployment to create")
    parser.add_argument("csar",
                        type=argparse.FileType("r"),
                        help="cloud service archive file")
    parser.set_defaults(func=deploy)


def deploy(args):
    inputs = yaml.safe_load(args.inputs) if args.inputs else {}
    csar.save(args.name, args.csar.name, inputs)

    print("Loading service template ...")
    service_template = types.ServiceTemplate.from_data(stdlib.load())
    service_template.merge(
        types.ServiceTemplate.from_data(yaml.safe_load(args.csar))
    )

    print("Resolving service template links ...")
    service_template.resolve()
    service_template.set_inputs(inputs)

    print("Creating instance model ...")
    instances = service_template.instantiate()

    print("Deploying instance model ...")
    instances.deploy()

    print("Done.")

    return 0
