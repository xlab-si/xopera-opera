import argparse

from opera.error import ParseError
from opera.log import get_logger

logger = get_logger()


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


# pylint: disable=unused-argument
def deploy(args):
    # csar.save(args.name, args.csar.name)
    status = 0

    logger.info("Loading service template ...")
    try:
        # ast = tosca.load(Path.cwd(), PurePath(args.csar.name))
        logger.info("=======================")
        # tmpl = template.build(ast)
        # logger.info(tmpl)
    except ParseError as e:
        logger.info("%s: %s", e.loc, e)
        status = 1

    #    logger.info("Resolving service template links ...")
    #    service_template.resolve()

    #    logger.info("Creating instance model ...")
    #    instances = service_template.instantiate()

    #    logger.info("Deploying instance model ...")
    #    instances.deploy()

    logger.info("Done.")

    return status
