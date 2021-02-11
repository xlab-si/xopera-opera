from opera.constants import OperationHost as Host
from opera.error import DataError
from opera.instance.base import Base


class Relationship(Base):
    def __init__(self, template, instance_id, source, target):
        super().__init__(template, instance_id)

        self.source = source
        self.target = target

    #
    # TOSCA functions
    #
    def get_attribute(self, params):
        host, attr, *rest = params

        valid_hosts = [i.value for i in Host]
        if host not in valid_hosts:
            raise DataError("Attribute host should be set to one of {}.".format(", ".join(valid_hosts)))

        if host == Host.SOURCE:
            return self.source.get_attribute([Host.SELF, attr] + rest)
        elif host == Host.TARGET:
            return self.target.get_attribute([Host.SELF, attr] + rest)

        # TODO(@tadeboro): Add support for nested attribute values once we
        # have data type support.
        if attr not in self.attributes:
            raise DataError("Instance has no '{}' attribute".format(attr))
        return self.attributes[attr].eval(self, attr)

    def get_property(self, params):
        host, prop, *rest = params

        valid_hosts = [i.value for i in Host]
        if host not in valid_hosts:
            raise DataError("Property host should be set to one of {}.".format(", ".join(valid_hosts)))

        if host == Host.SOURCE:
            return self.source.get_property([Host.SELF, prop] + rest)
        if host == Host.TARGET:
            return self.target.get_property([Host.SELF, prop] + rest)
        return self.template.get_property(params)

    def get_input(self, params):
        return self.template.get_input(params)

    def map_attribute(self, params, value):
        host, attr, *rest = params

        valid_hosts = [i.value for i in Host]
        if host not in valid_hosts:
            raise DataError("Attribute host should be set to one of {}.".format(", ".join(valid_hosts)))

        if host == Host.SOURCE:
            self.source.map_attribute([Host.SELF, attr] + rest, value)
        elif host == Host.TARGET:
            self.target.map_attribute([Host.SELF, attr] + rest, value)
        else:
            self.set_attribute(attr, value)

    def get_artifact(self, params):
        host, prop, *rest = params

        valid_hosts = [i.value for i in Host]
        if host not in valid_hosts:
            raise DataError("Artifact host should be set to one of {}.".format(", ".join(valid_hosts)))

        if host == Host.SOURCE:
            return self.source.get_property([Host.SELF, prop] + rest)
        if host == Host.TARGET:
            return self.target.get_property([Host.SELF, prop] + rest)
        return self.template.get_artifact(params)

    def concat(self, params):
        return self.template.concat(params)

    def join(self, params):
        return self.template.join(params)

    def token(self, params):
        return self.template.token(params)
