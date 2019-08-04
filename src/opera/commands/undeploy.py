import argparse

import yaml

from opera import csar, stdlib, types


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "undeploy",
        help="Undeploy service template"
    )
    parser.add_argument("name",
                        help="name of deployment to undeploy")
    parser.set_defaults(func=undeploy)


def undeploy(args):
    template_name = csar.load(args.name)

    print("Loading service template ...")
    service_template = types.ServiceTemplate.from_data(stdlib.load())
    with open(template_name) as fd:
        service_template.merge(
            types.ServiceTemplate.from_data(yaml.safe_load(fd))
        )

    print("Resolving service template links ...")
    service_template.resolve()

    print("Loading instance model ...")
    instances = service_template.instantiate()
    instances.load()

    print("Undeploying instance model ...")
    instances.undeploy()

    print("Done.")

    return 0
