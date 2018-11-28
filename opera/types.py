from __future__ import print_function, unicode_literals

from opera import ansible


class MissingImplementation(Exception):
    pass


def Pass(x):
    """
    Dummy "class" that can be used for types that do not need wrapping.
    """
    return x


class BaseEntity(object):
    def __repr__(self):
        return "{}[{}]".format(type(self).__name__, vars(self))

    def __str__(self):
        return self.dump(0)

    @staticmethod
    def dump_item(name, item, level):
        try:
            value = item.dump(level + 1)
            separator = "\n"
        except AttributeError:
            value = item  # pass-through for native types
            separator = " "

        return "{}{}:{}{}".format("  " * level, name, separator, value)


class Entity(BaseEntity):
    ATTRS = None  # This should be overridden in derived classes

    def check_override(self):
        if self.ATTRS is None:
            cls_name = self.__class__.__name__
            raise MissingImplementation(
                "{} did not override ATTRS".format(cls_name)
            )

    def __init__(self, data):
        self.check_override()
        for attr, cls in self.ATTRS.items():
            if attr in data:
                setattr(self, attr, cls(data[attr]))

    def dump(self, level):
        return "\n".join(
            self.dump_item(attr, getattr(self, attr), level)
            for attr in self.ATTRS if hasattr(self, attr)
        )


class EntityCollection(BaseEntity):
    ITEM_CLASS = None  # This should be overridden in derived classes

    def check_override(self):
        if self.ITEM_CLASS is None:
            cls_name = self.__class__.__name__
            raise MissingImplementation(
                "{} did not override ITEM_CLASS".format(cls_name)
            )

    def __init__(self, data):
        self.check_override()
        for k, v in data.items():
            setattr(self, k, self.ITEM_CLASS(v))

    def dump(self, level):
        return "\n".join(
            self.dump_item(k, v, level) for k, v in vars(self).items()
        )


class Interface(Entity):
    ATTRS = dict(
        create=Pass,
    )


class InterfaceCollection(EntityCollection):
    ITEM_CLASS = Interface


class NodeTemplate(Entity):
    ATTRS = dict(
        interfaces=InterfaceCollection,
        type=Pass,
    )

    def deploy(self):
        ansible.run(self.interfaces.Standard.create)


class NodeTemplateCollection(EntityCollection):
    ITEM_CLASS = NodeTemplate

    def deploy(self):
        # TODO(@tadeboro): Build graph here
        for v in vars(self).values():
            v.deploy()


class TopologyTemplate(Entity):
    ATTRS = dict(
        node_templates=NodeTemplateCollection,
    )

    def deploy(self):
        self.node_templates.deploy()


class ServiceTemplate(Entity):
    ATTRS = dict(
        topology_template=TopologyTemplate,
        tosca_definitions_version=Pass,
    )

    def deploy(self):
        self.topology_template.deploy()
