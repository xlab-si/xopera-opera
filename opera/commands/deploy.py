import argparse
import pkg_resources

import yaml

from opera import stdlib, types


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
    service_template = types.ServiceTemplate.from_data(stdlib.load())
    service_template.merge(
        types.ServiceTemplate.from_data(yaml.safe_load(args.csar))
    )

    service_template.resolve()
    # print(service_template)

    instances = service_template.instantiate()
    # print(instances)
    # print(instances.ordered_instance_ids)

    instances.deploy()
    return 0
