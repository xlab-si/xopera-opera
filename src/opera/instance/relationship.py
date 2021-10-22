from opera.constants import OperationHost
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

        if host == OperationHost.SELF.value:
            # TODO: Add support for nested attribute values once we have data type support.
            if attr not in self.attributes:
                raise DataError(
                    f"Instance has no '{attr}' attribute. Available attributes: {', '.join(self.attributes)}")
            return self.attributes[attr].eval(self, attr)
        elif host == OperationHost.SOURCE.value:
            return self.source.get_attribute([OperationHost.SELF.value, attr] + rest)
        elif host == OperationHost.TARGET.value:
            return self.target.get_attribute([OperationHost.SELF.value, attr] + rest)
        elif host == OperationHost.HOST.value:
            raise DataError(f"{host} keyword can be only used within node template context.")
        else:
            # try to find the attribute within the TOSCA nodes
            for node in self.template.topology.nodes.values():
                if host == node.name or host in node.types:
                    # TODO: Add support for nested attribute values.
                    if attr in node.attributes:
                        return node.attributes[attr].eval(self, attr)
            # try to find the attribute within the TOSCA relationships
            for rel in self.template.topology.relationships.values():
                if host == rel.name or host in rel.types:
                    # TODO: Add support for nested attribute values.
                    if attr in rel.attributes:
                        return rel.attributes[attr].eval(self, attr)

            raise DataError(
                f"We were unable to find the attribute: {attr} within the specified modelable entity or keyname: "
                f"{host} for relationship: {self.template.name}. The valid entities to get attributes from are "
                f"currently TOSCA nodes and relationships. But the best practice is that the attribute host is set to "
                f"'{OperationHost.SELF.value}'. This indicates that the attribute is referenced locally from something "
                f"in the relationship itself."
            )

    def get_property(self, params):
        host, prop, *rest = params

        if host == OperationHost.SOURCE.value:
            return self.source.get_property([OperationHost.SELF.value, prop] + rest)
        if host == OperationHost.TARGET.value:
            return self.target.get_property([OperationHost.SELF.value, prop] + rest)
        return self.template.get_property(params)

    def get_input(self, params):
        return self.template.get_input(params)

    def map_attribute(self, params, value):
        host, attr, *rest = params

        if host == OperationHost.SELF.value:
            # TODO: Add support for nested attribute values once we have data type support.
            if attr not in self.attributes:
                raise DataError(f"Cannot find attribute '{attr}' among {', '.join(self.attributes.keys())}.")
            self.set_attribute(attr, value)
        elif host == OperationHost.SOURCE.value:
            self.source.map_attribute([OperationHost.SELF.value, attr] + rest, value)
        elif host == OperationHost.TARGET.value:
            self.target.map_attribute([OperationHost.SELF.value, attr] + rest, value)
        else:
            raise DataError(
                f"Invalid attribute host for attribute mapping: {host}. For operation outputs in interfaces on "
                f"relationship templates, allowable keynames are: {OperationHost.SELF.value}, "
                f"{OperationHost.SOURCE.value}, or {OperationHost.TARGET.value}."
            )

    def get_artifact(self, params):
        host, prop, *rest = params

        valid_hosts = [i.value for i in OperationHost]
        if host not in valid_hosts:
            raise DataError(f"Artifact host should be set to one of {', '.join(valid_hosts)}. Was: {host}")

        if host == OperationHost.SOURCE.value:
            return self.source.get_property([OperationHost.SELF.value, prop] + rest)
        if host == OperationHost.TARGET.value:
            return self.target.get_property([OperationHost.SELF.value, prop] + rest)
        return self.template.get_artifact(params)

    def concat(self, params):
        return self.template.concat(params)

    def join(self, params):
        return self.template.join(params)

    def token(self, params):
        return self.template.token(params)
