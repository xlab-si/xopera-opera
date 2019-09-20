from opera.log import get_logger

logger = get_logger()


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "undeploy",
        help="Undeploy service template"
    )
    parser.add_argument("name",
                        help="name of deployment to undeploy")
    parser.set_defaults(func=undeploy)


def undeploy(args):
    ### template_name = csar.load(args.name)

    ### logger.info("Loading service template ...")
    ### service_template = types.ServiceTemplate.from_data(stdlib.load())
    ### with open(template_name) as fd:
    ###     service_template.merge(
    ###         types.ServiceTemplate.from_data(yaml.safe_load(fd))
    ###     )

    ### logger.info("Resolving service template links ...")
    ### service_template.resolve()

    ### logger.info("Loading instance model ...")
    ### instances = service_template.instantiate()
    ### instances.load()

    ### logger.info("Undeploying instance model ...")
    ### instances.undeploy()

    logger.info("Done.")

    return 0
